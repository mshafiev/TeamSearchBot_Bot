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

router = Router()

@router.message(F.text.lower() == "2 👤")
async def show_profile(message: Message, state: FSMContext, bot: Bot):
    """
    Отправляет пользователю его профиль.
    """
    user = client.get_user(tg_id=message.from_user.id)
    await func.send_user_profile(user, message, bot)
    await func.send_main_menu(message)

@router.message(F.text.lower() == "3 ✏️")
async def show_profile_edit_menu(message: Message, state: FSMContext):
    """
    Показывает меню редактирования профиля.
    """
    await message.answer(
        "Редактировать профиль",
        reply_markup=kb.my_profile_main
    )

@router.callback_query(F.data == "update_profile")
async def show_profile_edit_keyboard(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Показывает клавиатуру для редактирования профиля.
    """
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb.my_profile_edit_profile
    )

@router.callback_query(F.data == "update_olymps")
async def show_olymps_edit_keyboard(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Показывает клавиатуру для редактирования олимпиад.
    """
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=kb.my_profile_edit_olymps
    )

@router.callback_query(F.data == "update_back")
async def back_to_profile_menu(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Возвращает пользователя в главное меню редактирования профиля.
    """
    await callback_query.message.edit_text("Редактировать профиль:", reply_markup=kb.my_profile_main)

# ------- Профиль -------

@router.callback_query(F.data == "update_profile_update_first_name")
async def update_first_name_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новое имя.
    """
    await state.set_state(st.Registration.first_name)
    await func.send_message_by_tag("first_name", callback_query.message, state)
    await callback_query.answer("Изменение имени")

@router.callback_query(F.data == "update_profile_update_last_name")
async def update_last_name_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новую фамилию.
    """
    await state.set_state(st.Registration.last_name)
    await func.send_message_by_tag("last_name", callback_query.message, state)
    await callback_query.answer("Изменение фамилии")

@router.callback_query(F.data == "update_profile_update_middle_name")
async def update_middle_name_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новое отчество.
    """
    await state.set_state(st.Registration.middle_name)
    await func.send_message_by_tag("middle_name", callback_query.message, state)
    await callback_query.answer("Изменение отчества")

@router.callback_query(F.data == "update_profile_update_phone")
async def update_phone_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новый номер телефона.
    """
    await state.set_state(st.Registration.phone)
    await func.send_message_by_tag("phone", callback_query.message, state)
    await callback_query.answer("Изменение телефона")

@router.callback_query(F.data == "update_profile_update_age")
async def update_age_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новый возраст.
    """
    await state.set_state(st.Registration.age)
    await func.send_message_by_tag("age", callback_query.message, state)
    await callback_query.answer("Изменение возраста")

@router.callback_query(F.data == "update_profile_update_city")
async def update_city_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новый город.
    """
    await state.set_state(st.Registration.city)
    await func.send_message_by_tag("city", callback_query.message, state)
    await callback_query.answer("Изменение города")

@router.callback_query(F.data == "update_profile_update_status")
async def update_status_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новый статус отношений.
    """
    await state.set_state(st.Registration.status)
    await func.send_message_by_tag("status", callback_query.message, state)
    await callback_query.answer("Изменение статуса")

@router.callback_query(F.data == "update_profile_update_goal")
async def update_goal_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новую цель.
    """
    await state.set_state(st.Registration.goal)
    await func.send_message_by_tag("goal", callback_query.message, state)
    await callback_query.answer("Изменение цели")

@router.callback_query(F.data == "update_profile_update_who_interested")
async def update_who_interested_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя, кто его интересует.
    """
    await state.set_state(st.Registration.who_interested)
    await func.send_message_by_tag("who_interested", callback_query.message, state)
    await callback_query.answer("Изменение интересующих")

@router.callback_query(F.data == "update_profile_update_description")
async def update_description_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новое описание.
    """
    await state.set_state(st.Registration.description)
    await func.send_message_by_tag("description", callback_query.message, state)
    await callback_query.answer("Изменение описания")

@router.callback_query(F.data == "update_profile_update_date_of_birth")
async def update_date_of_birth_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новую дату рождения.
    """
    await state.set_state(st.Registration.date_of_birth)
    await func.send_message_by_tag("date_of_birth", callback_query.message, state)
    await callback_query.answer("Изменение даты рождения")

@router.callback_query(F.data == "update_profile_update_face_photo")
async def update_face_photo_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя новое селфи.
    """
    await state.set_state(st.Registration.face_photo)
    await func.send_message_by_tag("face_photo_id", callback_query.message, state)
    await callback_query.answer("Изменение селфи")

@router.callback_query(F.data == "update_profile_update_photo")
async def update_photo_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Запрашивает у пользователя дополнительное фото.
    """
    await state.set_state(st.Registration.photo)
    await func.send_message_by_tag("photo_id", callback_query.message, state)
    await callback_query.answer("Изменение дополнительного фото")

# ------- Олимпиады -------

@router.callback_query(F.data == "update_olymps_add_auto")
async def add_olymp_auto(callback_query: CallbackQuery, state: FSMContext):
    """
    Запускает автоматическую проверку олимпиад пользователя.
    """
    await callback_query.answer("Проверка началась, обычно это длится пару минут. Мы напишем вам как только закончим")

@router.callback_query(F.data == "update_olymps_add_other")
async def add_olymp_other(callback_query: CallbackQuery, state: FSMContext):
    """
    Запускает ручное добавление олимпиады: спрашивает название.
    """
    await state.set_state(st.AddOlymp.name)
    await callback_query.message.answer("Введите название олимпиады:")
    await callback_query.answer("Добавление олимпиады")

@router.message(st.AddOlymp.name)
async def olymp_add_name(message: Message, state: FSMContext):
    """
    Сохраняет название олимпиады и спрашивает профиль.
    """
    await state.update_data(name=message.text)
    await state.set_state(st.AddOlymp.profile)
    await message.answer("Введите профиль олимпиады:")

@router.message(st.AddOlymp.profile)
async def olymp_add_profile(message: Message, state: FSMContext):
    """
    Сохраняет профиль олимпиады и спрашивает год.
    """
    await state.update_data(profile=message.text)
    await state.set_state(st.AddOlymp.year)
    await message.answer("Введите год участия (например, 2023):")

@router.message(st.AddOlymp.year)
async def olymp_add_year(message: Message, state: FSMContext):
    """
    Сохраняет год олимпиады и спрашивает результат.
    """
    await state.update_data(year=message.text)
    await state.set_state(st.AddOlymp.result)
    await message.answer("Выберите результат:", reply_markup=kb.olymp_result)

@router.message(st.AddOlymp.result)
async def olymp_add_result(message: Message, state: FSMContext, bot: Bot):
    """
    Сохраняет результат олимпиады, отправляет данные на сервер и завершает добавление.
    """
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
            user_tg_id=message.from_user.id,
            level=0,  
            is_displayed=True
        )
        client.create_olymp(olymp)
        await message.answer("Олимпиада успешно добавлена!")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении олимпиады")
    await state.clear()
    
    user = client.get_user(tg_id=message.from_user.id)
    await func.send_user_profile(user, message, bot)
    await func.send_main_menu(message)

@router.callback_query(F.data == "update_olymps_update_visibility")
async def update_olymp_visibility(callback_query: CallbackQuery, state: FSMContext):
    """
    Показывает меню управления видимостью олимпиад пользователя.
    """
    user_id = callback_query.from_user.id
    user = client.get_user(user_id)
    olymp_buttons = await func.make_olymp_buttons(user)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=olymp_buttons)
    await callback_query.message.edit_text("Ваши олимпиады:", reply_markup=keyboard)

@router.callback_query(F.data == "update_olymps_visibility_back")
async def update_olymp_visibility_back(callback_query: CallbackQuery, state: FSMContext):
    """
    Возвращает пользователя в меню редактирования олимпиад.
    """
    await callback_query.message.edit_text("Меню олимпиад:", reply_markup=kb.my_profile_edit_olymps)
    await callback_query.answer("Вы вернулись в меню олимпиад")

@router.callback_query(F.data.startswith("toggle_olymp_visibility_"))
async def toggle_olymp_visibility_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Переключает видимость конкретной олимпиады пользователя.
    """
    olymp_id = callback_query.data.replace("toggle_olymp_visibility_", "")
    user_id = callback_query.from_user.id

    result = client.set_olymp_display(olymp_id)

    user = client.get_user(user_id)
    olymp_buttons = await func.make_olymp_buttons(user)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=olymp_buttons)
    await callback_query.message.edit_text("Ваши олимпиады:", reply_markup=keyboard)
