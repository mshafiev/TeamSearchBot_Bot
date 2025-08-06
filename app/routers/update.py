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
from api_client import APIClient
import app.keyboards as kb
import app.functions as func
from api_client import client, UserData

router = Router()

@router.message(F.text.lower() == "2 👤")
async def edit_profile_message(message: Message, state: FSMContext, bot: Bot):
    user = client.get_user(tg_id=message.from_user.id)
    await func.send_user_profile(user,message, bot)
    
@router.message(F.text.lower() == "3 ✏️")
async def edit_profile_message(message: Message, state: FSMContext):
    await message.answer(
        "Редактировать профиль",
        reply_markup=kb.my_profile_main
    )

@router.callback_query(F.data == "update_profile")
async def update_profile(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """Изменить профиль"""
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb.my_profile_edit_profile
    )
    
@router.callback_query(F.data == "update_olymps")
async def update_profile(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """Изменить профиль"""
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb.my_profile_edit_olymps
    )
    
@router.callback_query(F.data == "update_back")
async def update_back(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """Назад"""
    await callback_query.message.edit_text("Редактировать профиль:", reply_markup=kb.my_profile_main)


# ------- Профиль -------

@router.callback_query(F.data == "update_profile_update_first_name")
async def update_first_name_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.first_name)
    await func.send_message_by_tag("first_name", callback_query.message, state)
    await callback_query.answer("Изменение имени")

@router.callback_query(F.data == "update_profile_update_last_name")
async def update_last_name_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.last_name)
    await func.send_message_by_tag("last_name", callback_query.message, state)
    await callback_query.answer("Изменение фамилии")

@router.callback_query(F.data == "update_profile_update_middle_name")
async def update_middle_name_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.middle_name)
    await func.send_message_by_tag("middle_name", callback_query.message, state)
    await callback_query.answer("Изменение отчества")

@router.callback_query(F.data == "update_profile_update_phone")
async def update_phone_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.phone)
    await func.send_message_by_tag("phone", callback_query.message, state)
    await callback_query.answer("Изменение телефона")

@router.callback_query(F.data == "update_profile_update_age")
async def update_age_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.age)
    await func.send_message_by_tag("age", callback_query.message, state)
    await callback_query.answer("Изменение возраста")

@router.callback_query(F.data == "update_profile_update_city")
async def update_city_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.city)
    await func.send_message_by_tag("city", callback_query.message, state)
    await callback_query.answer("Изменение города")

@router.callback_query(F.data == "update_profile_update_status")
async def update_status_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.status)
    await func.send_message_by_tag("status", callback_query.message, state)
    await callback_query.answer("Изменение статуса")

@router.callback_query(F.data == "update_profile_update_goal")
async def update_goal_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.goal)
    await func.send_message_by_tag("goal", callback_query.message, state)
    await callback_query.answer("Изменение цели")

@router.callback_query(F.data == "update_profile_update_who_interested")
async def update_who_interested_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.who_interested)
    await func.send_message_by_tag("who_interested", callback_query.message, state)
    await callback_query.answer("Изменение интересующих")

@router.callback_query(F.data == "update_profile_update_description")
async def update_description_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.description)
    await func.send_message_by_tag("description", callback_query.message, state)
    await callback_query.answer("Изменение описания")

@router.callback_query(F.data == "update_profile_update_date_of_birth")
async def update_date_of_birth_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.date_of_birth)
    await func.send_message_by_tag("date_of_birth", callback_query.message, state)
    await callback_query.answer("Изменение даты рождения")

@router.callback_query(F.data == "update_profile_update_face_photo")
async def update_face_photo_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.face_photo)
    await func.send_message_by_tag("face_photo_id", callback_query.message, state)
    await callback_query.answer("Изменение селфи")

@router.callback_query(F.data == "update_profile_update_photo")
async def update_photo_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.Registration.photo)
    await func.send_message_by_tag("photo_id", callback_query.message, state)
    await callback_query.answer("Изменение дополнительного фото")

# ------- Олимпиады -------

@router.callback_query(F.data == "update_olymps_add_auto")
async def add_olymp_auto(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Проверка началась, обычно это длится пару минут. Мы напишем вам как только закончим")
    
    
@router.callback_query(F.data == "update_olymps_add_other")
async def add_olymp_other(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Пока не реализовано")
    
@router.callback_query(F.data == "update_olymps_update_visibility")
async def update_olymp_visibility(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user = client.get_user(user_id)
    olymp_buttons = await func.make_olymp_buttons(user)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=olymp_buttons)
    await callback_query.message.edit_text("Ваши олимпиады:", reply_markup=keyboard)

@router.callback_query(F.data == "update_olymps_visibility_back")
async def update_olymp_visibility_back(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Меню олимпиад:", reply_markup=kb.my_profile_edit_olymps)
    await callback_query.answer("Вы вернулись в меню олимпиад")


@router.callback_query(F.data.startswith("toggle_olymp_visibility_"))
async def toggle_olymp_visibility_callback(callback_query: CallbackQuery, state: FSMContext):
    olymp_id = callback_query.data.replace("toggle_olymp_visibility_", "")
    user_id = callback_query.from_user.id

    result = client.set_olymp_display(olymp_id)

    # Обновляем список олимпиад
    user = client.get_user(user_id)
    olymp_buttons = await func.make_olymp_buttons(user)
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=olymp_buttons)
    await callback_query.message.edit_text("Ваши олимпиады:", reply_markup=keyboard)
