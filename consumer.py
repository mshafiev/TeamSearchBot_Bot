import asyncio
import json
import os
from aio_pika import connect, IncomingMessage
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from app import texts

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def on_message(message: IncomingMessage):
    async with message.process():
        data = json.loads(message.body)
        tg_id = int(data.get("user_id", ""))
        await bot.send_message(chat_id=tg_id, text=texts.OLYMP_CHECK_SUCCESS)


async def main():
    RMQ_USER = os.getenv("RMQ_USER")
    RMQ_PASS = os.getenv("RMQ_PASS")
    RMQ_HOST = os.getenv("RMQ_HOST")
    RMQ_PORT = int(os.getenv("RMQ_PORT", 5672))

    connection = await connect(f"amqp://{RMQ_USER}:{RMQ_PASS}@{RMQ_HOST}:{RMQ_PORT}/")
    channel = await connection.channel()
    queue = await channel.declare_queue("olymps_success")

    await queue.consume(on_message)
    print(" [*] Waiting for messages...")

    await asyncio.Future()  # вечный таск


if __name__ == "__main__":
    asyncio.run(main())
