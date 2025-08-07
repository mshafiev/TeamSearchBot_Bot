import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import app.states as st
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from api_client import APIClient
import app.keyboards as kb
import app.functions as func
from api_client import client, UserData

router = Router()

@router.message(F.text.lower() == "заполнить анкету")
async def register_start(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик начала регистрации пользователя.
    Переводит пользователя в состояние ввода имени.
    """
    await state.set_state(st.Registration.first_name)
    await message.answer(
        "Как тебя зовут? (Имя)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(st.Registration.first_name)
async def register_first_name(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка имени пользователя.
    Сохраняет имя в состоянии и обновляет данные пользователя в базе.
    """
    await state.update_data(first_name=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                first_name=message.text[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.last_name)
async def register_last_name(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка фамилии пользователя.
    Сохраняет фамилию в состоянии и обновляет данные пользователя в базе.
    """
    await state.update_data(last_name=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                last_name=message.text[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.middle_name)
async def register_middle_name(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка отчества пользователя.
    Если пользователь ввёл "нет", отчество не сохраняется.
    """
    middle_name = "" if message.text.lower() == "нет" else message.text
    await state.update_data(middle_name=middle_name)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                middle_name=middle_name[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.phone)
async def register_phone(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка номера телефона пользователя.
    Ожидает контакт, иначе просит отправить номер через кнопку.
    """
    if not message.contact:
        await message.answer(
            "Нажмите на кнопку для отправки телефона"
        )
        return
    await state.update_data(phone=message.contact.phone_number)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                phone=message.contact.phone_number,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.description)
async def register_description(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка описания пользователя.
    Сохраняет описание и обновляет данные пользователя.
    """
    await state.update_data(description=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                description=message.text[:200],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.age)
async def register_age(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка возраста пользователя.
    Проверяет корректность возраста и обновляет данные.
    """
    try:
        age = int(message.text)
        if age < 14 or age > 100:
            await message.answer(
                "Возраст должен быть от 14 до 100 лет. Попробуй еще раз:"
            )
            return
        await state.update_data(age=age)
        try:
            client.update_user(
                UserData(
                    tg_id=message.from_user.id,
                    age=message.text,
                )
            )
        except Exception as e:
            print(e)
        user = client.get_user(tg_id=message.from_user.id)
        await func.update_user_data(user, message, state, bot)
    except ValueError:
        await message.answer("Пожалуйста, введи число. Попробуй еще раз:")
        return

@router.message(st.Registration.city)
async def register_city(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка города пользователя.
    Сохраняет город и обновляет данные пользователя.
    """
    await state.update_data(city=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                city=message.text[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.status)
async def register_status(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка статуса отношений пользователя.
    Сохраняет статус и обновляет данные пользователя.
    """
    status_map = {"нет": 0, "в отношениях": 1, "влюблен": 2}
    status = status_map.get(message.text.lower(), 0)
    await state.update_data(status=status)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                status=status,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.goal)
async def register_goal(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка цели пользователя.
    Сохраняет цель и обновляет данные пользователя.
    """
    goal_map = {"совместный бот": 0, "общение": 1, "поиск команды": 2, "отношения": 3}
    goal = goal_map.get(message.text.lower(), 1)
    await state.update_data(goal=goal)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                goal=goal,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.gender)
async def register_gender(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка гендер пользователя.
    Сохраняет гендер и обновляет данные пользователя.
    """
    
    interested_map = {"парень": False, "девушка": True}
    gender = interested_map.get(message.text.lower(), False)
    await state.update_data(gender=gender)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                gender=gender,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.who_interested)
async def register_who_interested(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка интересов пользователя (кого ищет).
    Сохраняет интересы и обновляет данные пользователя.
    """
    interested_map = {"женщины": 0, "мужчины": 1, "все": 2}
    who_interested = interested_map.get(message.text.lower(), 2)
    await state.update_data(who_interested=who_interested)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                who_interested=who_interested,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.date_of_birth)
async def register_date_of_birth(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка даты рождения пользователя и завершение регистрации.
    Проверяет формат даты и обновляет данные пользователя.
    """
    try:
        parts = message.text.split("-")
        if len(parts) != 3:
            raise ValueError("Неверный формат")
        day, month, year = map(int, parts)
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2024):
            raise ValueError("Неверные значения даты")
        await state.update_data(date_of_birth=message.text)
        try:
            client.update_user(
                UserData(
                    tg_id=message.from_user.id,
                    date_of_birth=message.text,
                )
            )
        except Exception as e:
            print(e)
        user = client.get_user(tg_id=message.from_user.id)
        await func.update_user_data(user, message, state, bot)
    except (ValueError, IndexError):
        await message.answer(
            "Неверный формат даты. Введи в формате ДД-ММ-ГГГГ (например: 15-03-1995):"
        )
        return

@router.message(st.Registration.face_photo, lambda message: message.photo)
async def register_selfi(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка селфи (фото лица) пользователя.
    Сохраняет file_id фотографии и обновляет данные пользователя.
    """
    if not message.photo:
        await message.answer("Неверный формат. Пожалуйста, отправьте фотографию (селфи).")
        return
    photo = message.photo[-1]
    file_id = str(photo.file_id)
    await state.update_data(face_photo_id=file_id)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                face_photo_id=file_id,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.photo)
async def register_photo(message: Message, state: FSMContext, bot: Bot):
    """
    Обработка дополнительного фото пользователя.
    Сохраняет file_id фотографии и обновляет данные пользователя.
    """
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фотографию.")
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(photo=file_id)
    try:
        client.update_user(
            UserData(
                tg_id=message.from_user.id,
                photo_id=file_id,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=message.from_user.id)
    await func.update_user_data(user, message, state, bot)