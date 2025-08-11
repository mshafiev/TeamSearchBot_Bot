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


router = Router()
recsys = RecSysClient()

@router.message(F.text.lower() == "смотреть анкеты 🚀")
async def view_questionnaires(message: Message, state: FSMContext, bot: Bot):
    """
    Начинает просмотр анкет - показывает первую рекомендацию
    """
    user = client.get_user(tg_id=str(message.from_user.id))
    user_id = str(message.from_user.id)
    ex = client.get_last_likes(str(message.from_user.id), 3)
    print(ex)
    excluded = []  
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
        await message.answer("Оцените анкету:", reply_markup=kb.rating_keyboard)
    else:
        await message.answer("К сожалению, пока нет подходящих анкет для вас 😔")

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "👍")
async def like_profile(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка лайка анкеты: отправка лайка в RMQ, уведомление адресата, проверка взаимности
    """
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    
    if not current_user_id:
        await message.answer("Ошибка: анкета не найдена")
        return

    # 1) Отправляем лайк в RabbitMQ
    await send_like_message(
        from_user_tg_id=str(message.from_user.id),
        to_user_tg_id=str(current_user_id),
        text=None,
        is_like=True,
        is_readed=False
    )

    # 2) Уведомляем адресата: "Ваша анкета кому-то понравилась" (если бот может писать ему)
    try:
        await bot.send_message(chat_id=current_user_id, text="Ваша анкета кому-то понравилась 💙", reply_markup=kb.incoming_likes_keyboard)
    except Exception:
        pass

    # 3) Проверяем взаимный лайк: существует ли лайк current_user_id -> from_user (True)
    try:
        exists_resp = client.like_exists(from_user_tg_id=str(current_user_id), to_user_tg_id=str(message.from_user.id), is_like=True)
        is_mutual = bool(exists_resp.get("exists"))
    except Exception:
        is_mutual = False

    if is_mutual:
        # Взаимная симпатия: отправляем обоим анкеты и телефоны
        me = client.get_user(tg_id=str(message.from_user.id))
        other = client.get_user(tg_id=str(current_user_id))
        # Мне — анкета собеседника + телефон
        await message.answer("Совпадение! У вас взаимная симпатия ✨")
        await func.send_user_profile(other, message, bot)
        if other.get("phone"):
            await message.answer(f"Его телефон: {other['phone']}")
        # Собеседнику — моя анкета + телефон
        try:
            await bot.send_message(chat_id=current_user_id, text="Совпадение! У вас взаимная симпатия ✨")
            dummy_msg = types.Message(message_id=0, date=message.date, chat=message.chat)
            await func.send_user_profile(me, dummy_msg, bot)
            if me.get("phone"):
                await bot.send_message(chat_id=current_user_id, text=f"Его телефон: {me['phone']}")
        except Exception:
            pass

    # 4) Переходим к следующей анкете
    await show_next_profile(message, state, bot)

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "👎")
async def dislike_profile(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка дизлайка анкеты
    """
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    
    if current_user_id:
        # Отправляем дизлайк в RabbitMQ
        await send_like_message(
            from_user_tg_id=str(message.from_user.id),
            to_user_tg_id=str(current_user_id),
            text=None,
            is_like=False,
            is_readed=False
        )
        
        await state.set_state(st.ViewingQuestionnaires.questionnaire)
        
        await message.answer("👎 Дизлайк отправлен!")
        await show_next_profile(message, state, bot)
    else:
        await message.answer("Ошибка: анкета не найдена")


@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "💤")
async def go_back(message: Message, state: FSMContext, bot: Bot):
    """
    Возврат в главное меню
    """
    await state.clear()
    await message.answer("Главное меню", reply_markup=kb.main)

@router.message(st.ViewingQuestionnaires.questionnaire, F.text == "✏️")
async def start_message_mode(message: Message, state: FSMContext, bot: Bot):
    """
    Переход в режим отправки сообщения с лайком
    """
    await state.set_state(st.ViewingQuestionnaires.message)
    await message.answer("Напишите сообщение, которое хотите отправить пользователю:", reply_markup=ReplyKeyboardRemove())

@router.message(st.ViewingQuestionnaires.message)
async def send_message_with_like(message: Message, state: FSMContext, bot: Bot):
    """
    Отправка лайка с пользовательским сообщением
    """
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    excluded_ids = data.get("excluded_ids", [])
    
    if current_user_id:
        # Отправляем лайк с сообщением в RabbitMQ
        await send_like_message(
            from_user_tg_id=str(message.from_user.id),
            to_user_tg_id=str(current_user_id),
            text=message.text,
            is_like=True,
            is_readed=False
        )
        await state.set_state(st.ViewingQuestionnaires.questionnaire)
        await message.answer(f"Сообщение отправлено!")
        await show_next_profile(message, state, bot)
    else:
        await message.answer("Ошибка: анкета не найдена")

async def show_next_profile(message: Message, state: FSMContext, bot: Bot):
    """
    Показывает следующую рекомендацию
    """
    ex = client.get_last_likes(str(message.from_user.id), 3)
    # Теперь предполагаем, что ex — это список словарей, где есть ключ 'to_user_tg_id'
    excluded_ids = [e['to_user_tg_id'] for e in ex] if ex else []
    user_id = str(message.from_user.id)
    # Получаем новую рекомендацию
    recommendation = recsys.get_recommendation(user_id, excluded_ids)
    
    if recommendation:
        rec_user = client.get_user(tg_id=recommendation)
        await state.update_data(current_user_id=recommendation)
        await func.send_user_profile(rec_user, message, bot)
        await message.answer("Оцените анкету:", reply_markup=kb.rating_keyboard)
    else:
        await message.answer("Больше анкет нет! Возвращаемся в главное меню.", reply_markup=kb.main)
        await state.clear()

@router.message(F.text == "Кому я понравился(ась) ❤️")
async def ask_incoming_likes(message: Message, state: FSMContext):
    await state.set_state(IncomingLikes.asking)
    await message.answer("Показать тех, кому вы понравились?", reply_markup=kb.incoming_likes_keyboard)

@router.message(F.text == "Показать, кому я понравился(ась) ❤️")
async def start_show_incoming_likes(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(IncomingLikes.viewing)
    await show_next_incoming_like(message, state, bot)

@router.message(IncomingLikes.asking, F.text == "Назад в меню")
async def back_from_ask(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=kb.main)

async def show_next_incoming_like(message: Message, state: FSMContext, bot: Bot):
    user_id = str(message.from_user.id)
    likes = client.get_incoming_likes(user_tg_id=user_id, only_unread=True, count=1)
    if not likes:
        await state.clear()
        await message.answer("Пока никто не лайкнул. Загляните позже.", reply_markup=kb.main)
        return
    like = likes[0]
    from_id = like.get("from_user_tg_id")
    liker = client.get_user(tg_id=from_id)
    # Сразу помечаем как прочитанный, раз показали пользователю
    try:
        client.set_like_readed(from_user_tg_id=str(from_id), to_user_tg_id=user_id)
    except Exception:
        pass
    await state.update_data(current_incoming_from_id=from_id)
    await func.send_user_profile(liker, message, bot)
    await message.answer("Поставить лайк в ответ?", reply_markup=incoming_like_reaction_keyboard)

@router.message(IncomingLikes.viewing, F.text == "Лайкнуть в ответ")
async def like_back_incoming(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    from_id = data.get("current_incoming_from_id")
    if not from_id:
        await message.answer("Ошибка: некого лайкнуть", reply_markup=kb.main)
        await state.clear()
        return
    # Проверяем взаимность (входящий лайк уже помечен как прочитанный)
    exists_resp = client.like_exists(from_user_tg_id=str(from_id), to_user_tg_id=str(message.from_user.id), is_like=True)
    is_mutual = bool(exists_resp.get("exists"))
    if is_mutual:
        me = client.get_user(tg_id=str(message.from_user.id))
        other = client.get_user(tg_id=str(from_id))
        await message.answer("Совпадение! У вас взаимная симпатия ✨")
        await func.send_user_profile(other, message, bot)
        if other.get("phone"):
            await message.answer(f"Его телефон: {other['phone']}")
        try:
            await bot.send_message(chat_id=str(from_id), text="Совпадение! У вас взаимная симпатия ✨")
            await func.send_user_profile_to_chat(me, chat_id=str(from_id), bot=bot)
            if me.get("phone"):
                await bot.send_message(chat_id=str(from_id), text=f"Его телефон: {me['phone']}")
        except Exception:
            pass
    else:
        # Отправляем лайк в ответ, если взаимности еще нет
        await send_like_message(
            from_user_tg_id=str(message.from_user.id),
            to_user_tg_id=str(from_id),
            text=None,
            is_like=True,
            is_readed=False
        )
        await message.answer("Лайк отправлен!")
    await show_next_incoming_like(message, state, bot)

@router.message(IncomingLikes.viewing, F.text == "Пропустить")
async def skip_incoming_like(message: Message, state: FSMContext, bot: Bot):
    # Лайк уже помечен как прочитанный при показе
    await show_next_incoming_like(message, state, bot)

@router.message(IncomingLikes.viewing, F.text == "Назад в меню")
async def back_from_viewing(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=kb.main)

