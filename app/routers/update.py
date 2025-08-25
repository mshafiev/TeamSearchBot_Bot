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
from app import texts
from producer import send_olymp_for_verification

router = Router()

@router.message(F.text.lower() == "2 👤")
async def show_profile(message: Message, state: FSMContext, bot: Bot):
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.send_user_profile(user, message, bot)
    await func.send_main_menu(message)

@router.message(F.text.lower() == "3 ✏️")
async def show_profile_edit_menu(message: Message, state: FSMContext):
    await message.answer(texts.EDIT_PROFILE_TITLE, reply_markup=kb.my_profile_main)


@router.callback_query(F.data == "delete_account")
async def delete_account(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    client.delete_user(callback_query.message.chat.id)
    await bot.send_message(chat_id=callback_query.message.chat.id, text="Аккаунт удален. Нажмите /start для начала работы")

@router.callback_query(F.data == "update_profile")
async def show_profile_edit_keyboard(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb.my_profile_edit_profile
    )

@router.callback_query(F.data == "update_olymps")
async def show_olymps_edit_keyboard(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb.my_profile_edit_olymps
    )

@router.callback_query(F.data == "update_back")
async def back_to_profile_menu(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.message.edit_text(texts.EDIT_PROFILE_TITLE + ":", reply_markup=kb.my_profile_main)

# ------- Профиль -------

@router.callback_query(F.data == "update_profile_update_first_name")
async def update_first_name_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("first_name", callback_query.message, state)
    await callback_query.answer("Изменение имени")

@router.callback_query(F.data == "update_profile_update_last_name")
async def update_last_name_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("last_name", callback_query.message, state)
    await callback_query.answer("Изменение фамилии")

@router.callback_query(F.data == "update_profile_update_middle_name")
async def update_middle_name_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("middle_name", callback_query.message, state)
    await callback_query.answer("Изменение отчества")

@router.callback_query(F.data == "update_profile_update_phone")
async def update_phone_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("phone", callback_query.message, state)
    await callback_query.answer("Изменение телефона")

@router.callback_query(F.data == "update_profile_update_age")
async def update_age_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("age", callback_query.message, state)
    await callback_query.answer("Изменение возраста")

@router.callback_query(F.data == "update_profile_update_city")
async def update_city_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("city", callback_query.message, state)
    await callback_query.answer("Изменение города")

@router.callback_query(F.data == "update_profile_update_status")
async def update_status_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("status", callback_query.message, state)
    await callback_query.answer("Изменение статуса")

@router.callback_query(F.data == "update_profile_update_goal")
async def update_goal_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("goal", callback_query.message, state)
    await callback_query.answer("Изменение цели")

@router.callback_query(F.data == "update_profile_update_who_interested")
async def update_who_interested_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("who_interested", callback_query.message, state)
    await callback_query.answer("Изменение интересующих")

@router.callback_query(F.data == "update_profile_update_description")
async def update_description_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("description", callback_query.message, state)
    await callback_query.answer("Изменение описания")

@router.callback_query(F.data == "update_profile_update_date_of_birth")
async def update_date_of_birth_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("date_of_birth", callback_query.message, state)
    await callback_query.answer("Изменение даты рождения")

@router.callback_query(F.data == "update_profile_update_face_photo")
async def update_face_photo_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("face_photo_id", callback_query.message, state)
    await callback_query.answer("Изменение селфи")

@router.callback_query(F.data == "update_profile_update_photo")
async def update_photo_callback(callback_query: CallbackQuery, state: FSMContext):
    await func.send_message_by_tag("photo_id", callback_query.message, state)
    await callback_query.answer("Изменение дополнительного фото")

# ------- Олимпиады -------

@router.callback_query(F.data == "update_olymps_add_auto")
async def add_olymp_auto(callback_query: CallbackQuery, state: FSMContext):
    user_data = client.get_user(tg_id=str(callback_query.from_user.id))
    await send_olymp_for_verification(
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        middle_name=user_data.get('middle_name'),
        date_of_birth=user_data.get('date_of_birth'),
        user_tg_id=str(callback_query.from_user.id)
    )
    await callback_query.message.answer(texts.OLYMP_CHECK_STARTED)
    await callback_query.answer(texts.OLYMP_CHECK_STARTED)

@router.callback_query(F.data == "update_olymps_add_other")
async def add_olymp_other(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(st.AddOlymp.name)
    await callback_query.message.answer("Введите название олимпиады:")
    await callback_query.answer("Добавление олимпиады")

@router.message(st.AddOlymp.name)
async def olymp_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(st.AddOlymp.profile)
    await message.answer("Введите профиль олимпиады:")

@router.message(st.AddOlymp.profile)
async def olymp_add_profile(message: Message, state: FSMContext):
    await state.update_data(profile=message.text)
    await state.set_state(st.AddOlymp.year)
    await message.answer("Введите год участия (например, 2023):")

@router.message(st.AddOlymp.year)
async def olymp_add_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(st.AddOlymp.result)
    await message.answer("Выберите результат:", reply_markup=kb.olymp_result)

@router.message(st.AddOlymp.result)
async def olymp_add_result(message: Message, state: FSMContext, bot: Bot):
    result_map = {
        "победитель": 0,
        "призер": 1,
        "финалист": 2,
        "участник": 3
    }
    result = result_map.get(message.text.lower(), 3)    
    await state.update_data(result=result)
    data = await state.get_data()
    try:
        olymp = OlympsData(
            name=data.get("name"),
            profile=data.get("profile"),
            year=data.get("year"),
            result=int(data.get("result")),
            user_tg_id=str(message.from_user.id),
            level=0,  
            is_displayed=True
        )
        client.create_olymp(olymp)
        await message.answer(texts.OLYMP_ADDED_OK)
    except Exception as e:
        await message.answer(f"{texts.OLYMP_ADD_ERR}")
    await state.clear()
    
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.send_user_profile(user, message, bot)
    await func.send_main_menu(message)

@router.callback_query(F.data == "update_olymps_update_visibility")
async def update_olymp_visibility(callback_query: CallbackQuery, state: FSMContext):
    user_id = str(callback_query.from_user.id)
    user = client.get_user(user_id)
    olymp_buttons = await func.make_olymp_buttons(user)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=olymp_buttons)
    await callback_query.message.edit_text(texts.EDIT_OLYMPS_TITLE, reply_markup=keyboard)

@router.callback_query(F.data == "update_olymps_visibility_back")
async def update_olymp_visibility_back(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(texts.EDIT_OLYMPS_MENU, reply_markup=kb.my_profile_edit_olymps)
    await callback_query.answer("Вы вернулись в меню олимпиад")

@router.callback_query(F.data.startswith("toggle_olymp_visibility_"))
async def toggle_olymp_visibility_callback(callback_query: CallbackQuery, state: FSMContext):
    olymp_id = callback_query.data.replace("toggle_olymp_visibility_", "")
    user_id = str(callback_query.from_user.id)

    result = client.set_olymp_display(olymp_id)

    user = client.get_user(user_id)
    olymp_buttons = await func.make_olymp_buttons(user)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=olymp_buttons)
    await callback_query.message.edit_text(texts.EDIT_OLYMPS_TITLE, reply_markup=keyboard)
