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

from app.utils import safe_send_media_group
from app import texts

register_fields = [
                ("first_name", st.Registration.first_name, texts.ASK_FIRST_NAME, kb.ReplyKeyboardRemove()),
                ("last_name", st.Registration.last_name, texts.ASK_LAST_NAME, kb.ReplyKeyboardRemove()),
                ("middle_name", st.Registration.middle_name, texts.ASK_MIDDLE_NAME, kb.ReplyKeyboardRemove()),
                ("phone", st.Registration.phone, texts.ASK_PHONE, kb.get_number),
                ("age", st.Registration.age, texts.ASK_AGE, kb.ReplyKeyboardRemove()),
                ("city", st.Registration.city, texts.ASK_CITY, kb.ReplyKeyboardRemove()),
                ("status", st.Registration.status, texts.ASK_STATUS, kb.wife_status),
                ("goal", st.Registration.goal, texts.ASK_GOAL, kb.goal),
                ("gender", st.Registration.gender, texts.ASK_GENDER, kb.gender),
                ("who_interested", st.Registration.who_interested, texts.ASK_WHO_INTERESTED, kb.who_interested),
                ("description", st.Registration.description, texts.ASK_DESCRIPTION, kb.ReplyKeyboardRemove()),
                ("date_of_birth", st.Registration.date_of_birth, texts.ASK_DATE_OF_BIRTH, kb.ReplyKeyboardRemove()),
                ("face_photo_id", st.Registration.face_photo, texts.ASK_FACE_PHOTO, kb.ReplyKeyboardRemove()),
                ("photo_id", st.Registration.photo, texts.ASK_EXTRA_PHOTO, kb.ReplyKeyboardRemove()),
            ]


async def get_user_profile(user):
    caption = f"{html.bold(user.get('first_name', 'Не указано'))}, {user.get('age', 'Не указано')}, {user.get('city', 'Не указано')} - {user.get('description', 'Не указано')}"
    olymps = user.get('olymps', [])
    visible_olymps = [o for o in olymps if o.get('is_displayed')]
    if visible_olymps:
        
        olymp_texts = []
        level_map = {
            0: "",
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
            level_str = level_map.get(level, str(level)) if isinstance(level, int) else str(level)
            result = olymp.get('result', '-')
            result_str = result_map.get(result, str(result)) if isinstance(result, int) else str(result)
            olymp_info = (
                f'<blockquote expandable="expandable"> {"✅ " if olymp.get("is_approved") else ""}{olymp.get("name", "Без названия")} {olymp.get("year", "-")}| '
                f'{olymp.get("profile", "-")}, '
                f'{level_str} уровень, '
                f'{result_str}</blockquote>'
            )
            olymp_texts.append(olymp_info)
        caption += "\n\nОлимпиады:\n" + "\n".join(olymp_texts)
    status_map = {
            0: "В отношениях",
            1: "Не в отношениях",
        }
    status_str = status_map.get(user.get('status', 'Не указано'), 'Не указано')
    caption += f"\n({status_str})"
    media_group = MediaGroupBuilder(caption=caption)
    if user.get('face_photo_id'):
        media_group.add_photo(media=user.get('face_photo_id'))
    if user.get('photo_id'):
        media_group.add_photo(media=user.get('photo_id'))
    return media_group


async def update_user_data(user, message: Message, state: FSMContext, bot: Bot):
    if any(value is None for value in user.values()):
            for field, state_field, text, kb_field in register_fields:
                if user.get(field) is None:
                    await state.set_state(state_field)
                    await message.answer(f"{text}", reply_markup=kb_field)
                    break
    else:
        await state.clear()
        await message.answer(texts.PROFILE_PREVIEW_TITLE)
        await send_user_profile(user, message, bot)
        await send_main_menu(message)
        return True
    
async def send_user_profile(user, message: Message, bot: Bot):
    media_group = await get_user_profile(user)
    await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())

async def send_user_profile_to_chat(user, chat_id: str, bot: Bot):
    media_group = await get_user_profile(user)
    await bot.send_media_group(chat_id=chat_id, media=media_group.build())

async def send_main_menu(message: Message):
    await message.answer(texts.MAIN_MENU_OPTIONS, reply_markup=kb.main)
   
async def send_message_by_tag(tag, message: Message, state: FSMContext):
    for field, state_field, text, kb_field in register_fields:
        if field == tag:
            await state.set_state(state_field)
            await message.answer(f"{text}", reply_markup=kb_field)
            return
    await message.answer("Не удалось найти поле для изменения.", reply_markup=kb.main)


async def make_olymp_buttons(user: api.UserData):
    olymp_buttons = []
    status_map = {
        0: "Победитель",
        1: "Призёр",
        2: "Финалист",
        3: "Участник"
    }
    for olymp in user.get("olymps", []):
        status_icon = "✅" if olymp.get("is_approved") else "❓"
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