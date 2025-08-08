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


router = Router()
recsys = RecSysClient()

@router.message(F.text.lower() == "смотреть анкеты 🚀")
async def view_questionnaires(message: Message, state: FSMContext, bot: Bot):
    """
    Начинает просмотр анкет - показывает первую рекомендацию
    """
    user = client.get_user(tg_id=message.from_user.id)
    user_id = message.from_user.id
    ex = client.get_last_likes(message.from_user.id, 3)
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
    Обработка лайка анкеты
    """
    data = await state.get_data()
    current_user_id = data.get("current_user_id")
    excluded_ids = data.get("excluded_ids", [])
    
    if current_user_id:
        # Отправляем лайк в RabbitMQ
        await send_like_message(
            from_user_tg_id=message.from_user.id,
            to_user_tg_id=current_user_id,
            text=None,
            is_like=True,
            is_readed=False
        )
        
        # Добавляем в исключения
        excluded_ids.append(str(current_user_id))
        await state.update_data(excluded_ids=excluded_ids)
        
        await message.answer("👍 Лайк отправлен!")
        await show_next_profile(message, state, bot)
    else:
        await message.answer("Ошибка: анкета не найдена")

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
            from_user_tg_id=message.from_user.id,
            to_user_tg_id=current_user_id,
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
            from_user_tg_id=message.from_user.id,
            to_user_tg_id=current_user_id,
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
    ex = client.get_last_likes(message.from_user.id, 3)
    # Теперь предполагаем, что ex — это список словарей, где есть ключ 'to_user_tg_id'
    excluded_ids = [int(e['to_user_tg_id']) for e in ex] if ex else []
    user_id = message.from_user.id
    # Получаем новую рекомендацию
    recommendation = recsys.get_recommendation(user_id, ",".join(str(e) for e in excluded_ids))
    
    if recommendation:
        rec_user = client.get_user(tg_id=recommendation)
        await state.update_data(current_user_id=recommendation)
        await func.send_user_profile(rec_user, message, bot)
        await message.answer("Оцените анкету:", reply_markup=kb.rating_keyboard)
    else:
        await message.answer("Больше анкет нет! Возвращаемся в главное меню.", reply_markup=kb.main)
        await state.clear()

