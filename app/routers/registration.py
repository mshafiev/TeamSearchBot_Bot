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
from app import texts
from app.validators import parse_age, parse_date_dmy

router = Router()

@router.message(F.text.lower() == "создать профиль")
async def register_start(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(st.Registration.first_name)
    await message.answer(texts.ASK_FIRST_NAME, reply_markup=ReplyKeyboardRemove())

@router.message(st.Registration.first_name)
async def register_first_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(first_name=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                first_name=message.text[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.last_name)
async def register_last_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(last_name=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                last_name=message.text[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.middle_name)
async def register_middle_name(message: Message, state: FSMContext, bot: Bot):
    middle_name = "" if message.text.lower() == "нет" else message.text
    await state.update_data(middle_name=middle_name)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                middle_name=middle_name[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)


@router.message(st.Registration.description)
async def register_description(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(description=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                description=message.text[:200],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.age)
async def register_age(message: Message, state: FSMContext, bot: Bot):
    age = parse_age(message.text)
    if age is None:
        try:
            int(message.text)
            await message.answer(texts.ERR_INVALID_AGE_RANGE)
        except Exception:
            await message.answer(texts.ERR_AGE_NOT_NUMBER)
        return
    await state.update_data(age=age)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                age=age,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.city)
async def register_city(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(city=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                city=message.text[:20],
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.status)
async def register_status(message: Message, state: FSMContext, bot: Bot):
    status_map = {"свободен(а)🔓": 0, "в отношениях 🔐": 1}
    status = status_map.get(message.text.lower(), 0)
    await state.update_data(status=status)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                status=status,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.goal)
async def register_goal(message: Message, state: FSMContext, bot: Bot):
    goal_map = {"совместный бот 📚": 0, "общение 💬": 1, "поиск команды 👥": 2, "отношения 💞": 3}
    goal = goal_map.get(message.text.lower(), 1)
    await state.update_data(goal=goal)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                goal=goal,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.gender)
async def register_gender(message: Message, state: FSMContext, bot: Bot):
    interested_map = {"парень": False, "девушка": True}
    gender = interested_map.get(message.text.lower(), False)
    await state.update_data(gender=gender)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                gender=gender,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.who_interested)
async def register_who_interested(message: Message, state: FSMContext, bot: Bot):
    interested_map = {"девушки 💋": 0, "парни 🎩": 1, "все": 2}
    who_interested = interested_map.get(message.text.lower(), 2)
    await state.update_data(who_interested=who_interested)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                who_interested=who_interested,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.date_of_birth)
async def register_date_of_birth(message: Message, state: FSMContext, bot: Bot):
    parsed = parse_date_dmy(message.text)
    if not parsed:
        await message.answer(texts.ERR_DATE_FORMAT)
        return
    await state.update_data(date_of_birth=message.text)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                date_of_birth=message.text,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.face_photo, lambda message: message.photo)
async def register_selfi(message: Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer(texts.ERR_NEED_SELFIE_PHOTO)
        return
    photo = message.photo[-1]
    file_id = str(photo.file_id)
    await state.update_data(face_photo_id=file_id)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                face_photo_id=file_id,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)

@router.message(st.Registration.photo)
async def register_photo(message: Message, state: FSMContext, bot: Bot):
    if not message.photo:
        await message.answer(texts.ERR_NEED_PHOTO)
        return
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(photo=file_id)
    try:
        client.update_user(
            UserData(
                tg_id=str(message.from_user.id),
                photo_id=file_id,
            )
        )
    except Exception as e:
        print(e)
    user = client.get_user(tg_id=str(message.from_user.id))
    await func.update_user_data(user, message, state, bot)