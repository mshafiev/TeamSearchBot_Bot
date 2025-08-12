
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
from app import texts

from api_client import client

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    user_id = str(message.from_user.id)
    user = None
    try:
        user = client.get_user(tg_id=user_id)
    except Exception:
        user = None
    
    if user:
        await func.update_user_data(user, message, state, bot)
        try:
            incoming = client.get_incoming_likes(user_tg_id=user_id, only_unread=True, count=1)
            if incoming:
                await message.answer(texts.WELCOME_EXISTING_USER_INCOMING_PROMPT, reply_markup=kb.incoming_likes_keyboard)
        except Exception:
            pass
    else:
        try:
            user = client.create_user(tg_id=user_id)
        except Exception:
            await message.answer(texts.ERROR_SERVER)
            return

        await message.answer(
            texts.WELCOME_NEW_USER.format(name=html.bold(message.from_user.full_name)),
            reply_markup=kb.start_reg,
        )

