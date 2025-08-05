import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types
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

from app.routers.registration import router as registration_router
from app.routers.start import router as start_router
from app.routers.update import router as update_router

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
DB_SERVER_HOST = getenv("DB_SERVER_HOST")
DB_SERVER_PORT = getenv("DB_SERVER_PORT")

client = APIClient(f"http://{DB_SERVER_HOST}:{DB_SERVER_PORT}")

async def main() -> None:
    dp = Dispatcher()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(update_router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
