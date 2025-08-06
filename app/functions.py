import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.utils.media_group import MediaGroupBuilder
import app.states as st
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from api_client import APIClient
import app.keyboards as kb
import api_client as api
import app.keyboards as kb

register_fields = [
                ("first_name", st.Registration.first_name, "Как тебя зовут? (Имя)", kb.ReplyKeyboardRemove()),
                ("last_name", st.Registration.last_name, "Ваша фамилия?", kb.ReplyKeyboardRemove()),
                ("middle_name", st.Registration.middle_name, "Ваше отчество? (Если нет — напишите 'нет')", kb.ReplyKeyboardRemove()),
                ("phone", st.Registration.phone, "Ваш номер телефона?", kb.get_number),
                ("age", st.Registration.age, "Сколько вам лет?", kb.ReplyKeyboardRemove()),
                ("city", st.Registration.city, "В каком городе вы живёте?", kb.ReplyKeyboardRemove()),
                ("status", st.Registration.status, "Ваш статус: 0 — свободен, 1 — в отношениях", kb.wife_status),
                ("goal", st.Registration.goal, "Ваша цель: 0 — совместный бот, 1 — общение, 2 — поиск команды, 3 — отношения", kb.goal),
                ("who_interested", st.Registration.who_interested, "Кто вам интересен: 0 — девушки, 1 — парни, 2 — все", kb.who_interested),
                ("description", st.Registration.description, "Описание для профиля (например ищу девушку блондинку)", kb.ReplyKeyboardRemove()),
                ("date_of_birth", st.Registration.date_of_birth, "Ваша дата рождения (ДД-ММ-ГГГГ)", kb.ReplyKeyboardRemove()),
                ("face_photo_id", st.Registration.face_photo, "Пожалуйста, отправьте селфи (фото лица)", kb.ReplyKeyboardRemove()),
                ("photo_id", st.Registration.photo, "Пожалуйста, отправьте дополнительное фото", kb.ReplyKeyboardRemove()),
            ]


async def get_user_profile(user):
    # Формируем основной caption профиля
    caption = f"{html.bold(user.get('first_name', 'Не указано'))}, {user.get('age', 'Не указано')}, {user.get('city', 'Не указано')} - {user.get('description', 'Не указано')}"
    
    # Добавляем олимпиады, если есть видимые
    olymps = user.get('olymps', [])
    visible_olymps = [o for o in olymps if o.get('is_displayed')]
    if visible_olymps:
        olymp_texts = []
        level_map = {
            0: "Не Рсош",
            1: "1",
            2: "2",
            3: "3"
        }
        result_map = {
            0: "Победитель",
            1: "Призёр",
            2: "Финалист",
            3: "Участник"
        }
        for olymp in visible_olymps:
            level = olymp.get('level', '-')
            if isinstance(level, int):
                level_str = level_map.get(level, str(level))
            else:
                level_str = str(level)
            result = olymp.get('result', '-')
            if isinstance(result, int):
                result_str = result_map.get(result, str(result))
            else:
                result_str = str(result)
            olymp_info = (
                f"<blockquote> {"✅" if olymp.get('is_approved') else "❌"} {olymp.get('name', 'Без названия')} | "
                f"Профиль: {olymp.get('profile', '-')}, "
                f"Год: {olymp.get('year', '-')}, "
                f"Уровень: {level_str}, "
                f"Результат: {result_str}</blockquote>"
            )
            # Оформляем как цитату (quote) в Telegram
            olymp_texts.append(olymp_info)
        caption += "\n\nОлимпиады:\n" + "\n".join(olymp_texts)

    media_group = MediaGroupBuilder(
        caption=caption
    )
    media_group.add_photo(media=user.get('face_photo_id'))
    media_group.add_photo(media=user.get('photo_id'))
    return media_group


async def update_user_data(user, message: Message, state: FSMContext, bot: Bot):
    print(user)
    if any(value is None for value in user.values()):
            for field, state_field, text, kb_field in register_fields:
                if user.get(field) is None:
                    await state.set_state(state_field)
                    await message.answer(f"{text}", reply_markup=kb_field)
                    break
    else:
        await state.clear()
        await message.answer("Твоя анкета выглядит так:")
        await send_user_profile(user, message, bot)
        await send_main_menu(message)
        return True
    
async def send_user_profile(user, message: Message, bot: Bot):
    media_group = await get_user_profile(user)
    
    await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())

async def send_main_menu(message: Message):
    await message.answer(
        "1. Смотреть анкеты. \n2. Моя анкета. \n3. Редактировать профиль",
        reply_markup=kb.main
    )
   
async def send_message_by_tag(tag, message: Message, state: FSMContext):
    """
    Отправляет сообщение пользователю по тегу из register_fields.
    :param tag: str - тег (название поля) из register_fields
    :param message: Message - объект сообщения
    :param state: FSMContext - состояние пользователя
    """
    for field, state_field, text, kb_field in register_fields:
        if field == tag:
            await state.set_state(state_field)
            await message.answer(f"{text}", reply_markup=kb_field)
            return
    await message.answer("Не удалось найти поле для изменения.", reply_markup=kb.main)


async def make_olymp_buttons(user: api.UserData):
    olymp_buttons = []
    print(user)
    status_map = {
        0: "Победитель",
        1: "Призёр",
        2: "Финалист",
        3: "Участник"
    }
    for olymp in user.get("olymps", []):
        status_icon = "✅" if olymp.get("is_approved") else "❌"
        visibility_icon = "👁️" if olymp.get("is_displayed") else ""
        status_num = olymp.get("result")
        status_text = status_map.get(status_num, f"Статус {status_num}")
        year = olymp.get("year", "")
        button_text = f"{visibility_icon} {status_icon} {olymp.get('name')} ({status_text}, {year})"
        olymp_buttons.append([types.InlineKeyboardButton(
            text=button_text, 
            callback_data=f"toggle_olymp_visibility_{olymp.get('id')}"
        )])
    back_button = [types.InlineKeyboardButton(
        text="Назад",
        callback_data="update_olymps_visibility_back"
    )]
    olymp_buttons.append(back_button)
    return olymp_buttons