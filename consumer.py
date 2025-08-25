from pika import ConnectionParameters, BlockingConnection, PlainCredentials
import os
from dotenv import load_dotenv
import json
from aiogram import Bot
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app import texts

from app.routers.registration import router as registration_router
from app.routers.start import router as start_router
from app.routers.update import router as update_router
from app.routers.questionnaires import router as questionnaires_router


load_dotenv()

RMQ_USER = os.getenv("RMQ_USER")
RMQ_PASS = os.getenv("RMQ_PASS")
RMQ_HOST = os.getenv("RMQ_HOST")
RMQ_PORT = int(os.getenv("RMQ_PORT", 5672))
DB_HOST = os.getenv("DB_SERVER_HOST")
DB_PORT = os.getenv("DB_SERVER_PORT")

credentials = PlainCredentials(RMQ_USER, RMQ_PASS)

connection_params = ConnectionParameters(
    host=RMQ_HOST,
    port=RMQ_PORT,
    credentials=credentials,
)

load_dotenv()
TOKEN = getenv("BOT_TOKEN")


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        tg_id = data.get("user_id", "")
        bot.send_message(
            chat_id=int(tg_id),  
            text=texts.OLYMP_CHECK_SUCCESS
        )
    except Exception as e:
       print(e)

def main():
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="olymps_success")

            ch.basic_consume(
                queue="olymps_success",
                on_message_callback=callback,
            )
            ch.start_consuming()

if __name__ == "__main__":
    main()
