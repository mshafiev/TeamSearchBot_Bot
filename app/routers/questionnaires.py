import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery
import app.states as st
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from api_client import APIClient, OlympsData
import app.keyboards as kb
import app.functions as func
from api_client import client, UserData
from recsys_client import RecSysClient
from producer import send_like_message
from app.states import IncomingLikes
from app.keyboards import incoming_like_reaction_keyboard
from app import texts
from app.validators import is_valid_user_id, validate_message_text
from app.utils import safe_send_message


router = Router()
recsys = RecSysClient()

@router.message(F.text.lower() == "🚀")
async def view_questionnaires(message: Message, state: FSMContext, bot: Bot):
    user_id = str(message.from_user.id)
    user = client.get_user(tg_id=user_id)
    ex = client.get_last_likes(user_id, 3)
    excluded = [e['to_user_tg_id'] for e in ex] if ex else []
    recommendation = recsys.get_recommendation(user_id, excluded)
    if recommendation:
        rec_user = client.get_user(tg_id=recommendation)
        await state.update_data(
            current_user_id=recommendation, 
            excluded_ids=excluded,
            user_id=user_id
        )
        await state.set_state(st.ViewingQuestionnaires.questionnaire)
        await func.send_user_profile(rec_user, message, bot)
        await message.answer(texts.RATE_PROFILE_PROMPT, reply_markup=kb.rating_keyboard)
    else:
        await message.answer(texts.NO_MATCHES_AVAILABLE)

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "❤️")
async def like_profile(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    if not is_valid_user_id(current_user_id):
        await message.answer(texts.ERROR_PROFILE_NOT_FOUND)
        return

    await send_like_message(
        from_user_tg_id=str(message.from_user.id),
        to_user_tg_id=str(current_user_id),
        text=None,
        is_like=True,
        is_readed=False
    )

    await safe_send_message(bot, chat_id=current_user_id, text=texts.SOMEONE_LIKED_YOU, reply_markup=kb.incoming_likes_keyboard)

    try:
        exists_resp = client.like_exists(from_user_tg_id=str(current_user_id), to_user_tg_id=str(message.from_user.id), is_like=True)
        is_mutual = bool(exists_resp.get("exists"))
    except Exception:
        is_mutual = False

    if is_mutual:
        me = client.get_user(tg_id=str(message.from_user.id))
        other = client.get_user(tg_id=str(current_user_id))
        await message.answer(texts.MUTUAL_LIKE)
        await func.send_user_profile(other, message, bot)
        if other.get("username"):
            await message.answer(texts.PHONE_OF_USER.format(phone=other["username"]))
        try:
            await safe_send_message(bot, chat_id=current_user_id, text=texts.MUTUAL_LIKE)
            dummy_msg = types.Message(message_id=0, date=message.date, chat=message.chat)
            await func.send_user_profile(me, dummy_msg, bot)
            if me.get("username"):
                await safe_send_message(bot, chat_id=current_user_id, text=texts.PHONE_OF_USER.format(phone=me["username"]))
        except Exception:
            pass

    await show_next_profile(message, state, bot)

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "👎")
async def dislike_profile(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    if not is_valid_user_id(current_user_id):
        await message.answer(texts.ERROR_PROFILE_NOT_FOUND)
        return

    await send_like_message(
        from_user_tg_id=str(message.from_user.id),
        to_user_tg_id=str(current_user_id),
        text=None,
        is_like=False,
        is_readed=False
    )

    await state.set_state(st.ViewingQuestionnaires.questionnaire)
    await message.answer(texts.DISLIKE_SENT)
    await show_next_profile(message, state, bot)

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "главное меню")
async def go_back(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer(texts.MAIN_MENU_TITLE, reply_markup=kb.main)

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "💬")
async def start_message_mode(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(st.ViewingQuestionnaires.message)
    await message.answer(texts.ASK_CUSTOM_MESSAGE, reply_markup=ReplyKeyboardRemove())

@router.message(st.ViewingQuestionnaires.message)
async def send_message_with_like(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(st.ViewingQuestionnaires.questionnaire)
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    if not is_valid_user_id(current_user_id):
        await message.answer(texts.ERROR_PROFILE_NOT_FOUND)
        return

    ok, cleaned = validate_message_text(message.text)
    if not ok:
        await message.answer(texts.LIKE_WITH_MESSAGE_SENT)
        cleaned = None

    await send_like_message(
        from_user_tg_id=str(message.from_user.id),
        to_user_tg_id=str(current_user_id),
        text=cleaned,
        is_like=True,
        is_readed=False
    )
    await safe_send_message(bot, chat_id=current_user_id, text=texts.SOMEONE_LIKED_YOU, reply_markup=kb.incoming_likes_keyboard)

    try:
        exists_resp = client.like_exists(from_user_tg_id=str(current_user_id), to_user_tg_id=str(message.from_user.id), is_like=True)
        is_mutual = bool(exists_resp.get("exists"))
    except Exception:
        is_mutual = False

    if is_mutual:
        me = client.get_user(tg_id=str(message.from_user.id))
        other = client.get_user(tg_id=str(current_user_id))
        await message.answer(texts.MUTUAL_LIKE)
        await func.send_user_profile(other, message, bot)
        if other.get("username"):
            await message.answer(texts.PHONE_OF_USER.format(phone=other["username"]))
        try:
            await safe_send_message(bot, chat_id=current_user_id, text=texts.MUTUAL_LIKE)
            dummy_msg = types.Message(message_id=0, date=message.date, chat=message.chat)
            await func.send_user_profile(me, dummy_msg, bot)
            if me.get("username"):
                await safe_send_message(bot, chat_id=current_user_id, text=texts.PHONE_OF_USER.format(phone=me["username"]))
        except Exception:
            pass

    await show_next_profile(message, state, bot)

async def show_next_profile(message: Message, state: FSMContext, bot: Bot):
    ex = client.get_last_likes(str(message.from_user.id), 25)
    print(ex)
    excluded_ids = [e['to_user_tg_id'] for e in ex] if ex else []
    print(excluded_ids)
    user_id = str(message.from_user.id)
    recommendation = recsys.get_recommendation(user_id, excluded_ids)
    if recommendation:
        rec_user = client.get_user(tg_id=recommendation)
        await state.update_data(current_user_id=recommendation)
        await func.send_user_profile(rec_user, message, bot)
        await message.answer(texts.RATE_PROFILE_PROMPT, reply_markup=kb.rating_keyboard)
    else:
        await message.answer(texts.NO_MORE_PROFILES, reply_markup=kb.main)
        await state.clear()

@router.message(F.text == "Кому я понравился(ась) ❤️")
async def ask_incoming_likes(message: Message, state: FSMContext):
    await state.set_state(IncomingLikes.asking)
    await message.answer(texts.INCOMING_LIKES_PROMPT, reply_markup=kb.incoming_likes_keyboard)

@router.message(F.text == "Показать, кому я понравился(ась) ❤️")
async def start_show_incoming_likes(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(IncomingLikes.viewing)
    await show_next_incoming_like(message, state, bot)

@router.message(IncomingLikes.asking, F.text == "Назад в меню")
async def back_from_ask(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.MAIN_MENU_TITLE, reply_markup=kb.main)

async def show_next_incoming_like(message: Message, state: FSMContext, bot: Bot):
    user_id = str(message.from_user.id)
    likes = client.get_incoming_likes(user_tg_id=user_id, only_unread=True, count=1)
    if not likes:
        await state.clear()
        await message.answer(texts.INCOMING_LIKES_EMPTY, reply_markup=kb.main)
        return
    like = likes[0]
    from_id = like.get("from_user_tg_id")
    liker = client.get_user(tg_id=from_id)
    try:
        client.set_like_readed(from_user_tg_id=str(from_id), to_user_tg_id=user_id)
    except Exception:
        pass
    await state.update_data(current_incoming_from_id=from_id)
    await func.send_user_profile(liker, message, bot)
    try:
        await message.answer("Сообщение для тебя:\n"+like.get("text"))
    except:
        pass
    await message.answer(texts.INCOMING_LIKE_ASK_BACK, reply_markup=incoming_like_reaction_keyboard)

@router.message(IncomingLikes.viewing, F.text == "💋")
async def like_back_incoming(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    from_id = data.get("current_incoming_from_id")
    if not is_valid_user_id(from_id):
        await message.answer(texts.ERROR_NOTHING_TO_LIKE, reply_markup=kb.main)
        await state.clear()
        return
    
    # Отмечаем лайк как прочитанный
    try:
        client.set_like_readed(from_user_tg_id=str(from_id), to_user_tg_id=str(message.from_user.id))
    except Exception:
        pass
    
    exists_resp = client.like_exists(from_user_tg_id=str(from_id), to_user_tg_id=str(message.from_user.id), is_like=True)
    is_mutual = bool(exists_resp.get("exists"))
    if is_mutual:
        me = client.get_user(tg_id=str(message.from_user.id))
        other = client.get_user(tg_id=str(from_id))
        await message.answer(texts.MUTUAL_LIKE)
        await func.send_user_profile(other, message, bot)
        if other.get("username"):
            await message.answer(texts.PHONE_OF_USER.format(phone=other["username"]))
        try:
            await safe_send_message(bot, chat_id=str(from_id), text=texts.MUTUAL_LIKE)
            await func.send_user_profile_to_chat(me, chat_id=str(from_id), bot=bot)
            if me.get("username"):
                await safe_send_message(bot, chat_id=str(from_id), text=texts.PHONE_OF_USER.format(phone=me["username"]))
        except Exception:
            pass
    else:
        await send_like_message(
            from_user_tg_id=str(message.from_user.id),
            to_user_tg_id=str(from_id),
            text=None,
            is_like=True,
            is_readed=False
        )
        await message.answer(texts.LIKE_SENT)
    await show_next_incoming_like(message, state, bot)

@router.message(IncomingLikes.viewing, F.text == "👎")
async def skip_incoming_like(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    from_id = data.get("current_incoming_from_id")
    
    # Отмечаем лайк как прочитанный
    if is_valid_user_id(from_id):
        try:
            client.set_like_readed(from_user_tg_id=str(from_id), to_user_tg_id=str(message.from_user.id))
        except Exception:
            pass
    
    await show_next_incoming_like(message, state, bot)

@router.message(IncomingLikes.viewing, F.text == "Назад в меню")
async def back_from_viewing(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.MAIN_MENU_TITLE, reply_markup=kb.main)

