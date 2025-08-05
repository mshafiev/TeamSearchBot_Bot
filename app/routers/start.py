
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
import app.functions as func

from api_client import client

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработчик команды /start
    Проверяет наличие пользователя в БД и предлагает регистрацию
    """
    user_id = message.from_user.id
    print(user_id)

    user = client.get_user(tg_id=user_id)
    
    if user:
        await func.update_user_data(user, message, state, bot)
    else:
        try:
            user = client.create_user(tg_id=user_id)
        except:
            await message.answer("На сервере произошла ошибка")
            return

        await message.answer(
            f"Привет, {html.bold(message.from_user.full_name)}!\n"
            f"Добро пожаловать в бот знакомств!\n"
            f"Для начала работы нужно пройти регистрацию.\n"
            f"Нажми на кнопку ниже, чтобы начать:",
            reply_markup=kb.start_reg,
        )

