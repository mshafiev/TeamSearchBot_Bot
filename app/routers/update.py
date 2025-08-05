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

@router.callback_query(F.data == "update_profile")
async def register_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Изменить профиль"""
    
    
