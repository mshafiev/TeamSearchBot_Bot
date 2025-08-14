from pika import ConnectionParameters, BlockingConnection, PlainCredentials
import os
import json
from typing import Optional
from dotenv import load_dotenv
import logging
import asyncio

from app.validators import is_valid_user_id, validate_message_text


logging.getLogger("pika").setLevel(logging.WARNING)


load_dotenv()

RMQ_USER = os.getenv("RMQ_USER")
RMQ_PASS = os.getenv("RMQ_PASS")
RMQ_HOST = os.getenv("RMQ_HOST")
RMQ_PORT = int(os.getenv("RMQ_PORT", 5672))

credentials = PlainCredentials(RMQ_USER, RMQ_PASS)

connection_params = ConnectionParameters(
    host=RMQ_HOST,
    port=RMQ_PORT,
    credentials=credentials,
)


def _send_like_message_sync(message_data: dict) -> bool:
    try:
        with BlockingConnection(connection_params) as conn:
            with conn.channel() as ch:
                ch.queue_declare(queue="likes")
                ch.basic_publish(
                    exchange="",
                    routing_key="likes",
                    body=json.dumps(message_data)
                )
                logging.info("Like message enqueued: %s", message_data)
                return True
    except Exception as exc:
        logging.error("RMQ publish failed: %s", exc)
        return False


async def send_like_message(
    from_user_tg_id: str,
    to_user_tg_id: str,
    text: Optional[str] = None,
    is_like: bool = False,
    is_readed: bool = False
) -> bool:
    """
    Enqueue like/dislike event to RabbitMQ without blocking the event loop.
    Validates user ids and message text.
    """
    if not is_valid_user_id(from_user_tg_id) or not is_valid_user_id(to_user_tg_id):
        logging.warning(
            "Invalid user ids for like message: from=%s to=%s",
            from_user_tg_id,
            to_user_tg_id,
        )
        return False

    ok, cleaned_text = validate_message_text(text)
    message_text = cleaned_text if ok else None

    message_data = {
        "from_user_tg_id": str(from_user_tg_id),
        "to_user_tg_id": str(to_user_tg_id),
        "text": message_text,
        "is_like": bool(is_like),
        "is_readed": bool(is_readed),
    }

    return await asyncio.to_thread(_send_like_message_sync, message_data)

async def send_olymp_for_verification(
    first_name: str,
    last_name: str,
    middle_name: str,
    date_of_birth: str,
    user_tg_id: str
) -> bool:
    """
    Отправляет данные олимпиады на проверку в очередь RabbitMQ.
    """
    message_data = {
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "date_of_birth": date_of_birth,
        "user_tg_id": user_tg_id
    }

    try:
        with BlockingConnection(connection_params) as conn:
            with conn.channel() as ch:
                ch.queue_declare(queue="olymps")
                ch.basic_publish(
                    exchange="",
                    routing_key="olymps",
                    body=json.dumps(message_data)
                )
                logging.info("Olymp message enqueued: %s", message_data)
                return True
    except Exception as exc:
        logging.error("RMQ publish failed: %s", exc)
        return False




def main():
    # Example usage (synchronous context)
    success = asyncio.run(
        send_like_message(
            from_user_tg_id="1",
            to_user_tg_id="10",
            text="Привет!",
            is_like=True,
            is_readed=False,
        )
    )

    if success:
        print("Message sent successfully")
    else:
        print("Failed to send message")


if __name__ == "__main__":
    main()