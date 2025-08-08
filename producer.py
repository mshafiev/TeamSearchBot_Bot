from pika import ConnectionParameters, BlockingConnection, PlainCredentials
import os
import json
from typing import Optional
from dotenv import load_dotenv
import logging


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


async def send_like_message(
    from_user_tg_id: int,
    to_user_tg_id: int,
    text: Optional[str] = None,
    is_like: bool = False,
    is_readed: bool = False
) -> bool:
    """
    Отправляет сообщение о лайке/дизлайке в RabbitMQ.
    
    Args:
        from_user_tg_id: ID пользователя, который отправляет лайк
        to_user_tg_id: ID пользователя, которому отправляется лайк
        text: Текст сообщения (опционально)
        is_like: True для лайка, False для дизлайка
        is_readed: Статус прочтения сообщения
    
    Returns:
        bool: True если сообщение отправлено успешно, False в случае ошибки
    """
    message_data = {
        "from_user_tg_id": from_user_tg_id,
        "to_user_tg_id": to_user_tg_id,
        "text": text,
        "is_like": is_like,
        "is_readed": is_readed
    }
    
    try:
        with BlockingConnection(connection_params) as conn:
            with conn.channel() as ch:
                ch.queue_declare(queue="likes")
                
                ch.basic_publish(
                    exchange="",
                    routing_key="likes",
                    body=json.dumps(message_data)
                )
                print(f"Message sent: {message_data}")
                return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def main():
    # Пример использования
    success = send_like_message(
        from_user_tg_id=1,
        to_user_tg_id=10,
        text="Привет!",
        is_like=True,
        is_readed=False
    )
    
    if success:
        print("Message sent successfully")
    else:
        print("Failed to send message")
            
            
if __name__ == "__main__":
    main()