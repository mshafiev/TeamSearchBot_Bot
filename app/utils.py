import logging
from typing import Optional
from aiogram import Bot, types


async def safe_send_message(bot: Bot, chat_id: str, text: str, reply_markup: Optional[types.ReplyKeyboardMarkup | types.InlineKeyboardMarkup] = None) -> bool:
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
        return True
    except Exception as exc:
        logging.warning("send_message failed for chat_id=%s: %s", chat_id, exc)
        return False


async def safe_send_media_group(bot: Bot, chat_id: str, media: list[types.InputMediaPhoto]) -> bool:
    try:
        await bot.send_media_group(chat_id=chat_id, media=media)
        return True
    except Exception as exc:
        logging.warning("send_media_group failed for chat_id=%s: %s", chat_id, exc)
        return False