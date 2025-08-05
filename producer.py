from pika import ConnectionParameters, BlockingConnection, PlainCredentials
import os
from dotenv import load_dotenv

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


json = """{
  "from_user_tg_id": 1,
  "to_user_tg_id": 10,
  "text": null,
  "is_like": false,
  "is_readed": false
}"""

def main():
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="likes")
            
            ch.basic_publish(
                exchange="",
                routing_key="likes",
                body=f"{json}"
            )
            print("Message sent")
            
            
if __name__ == "__main__":
    main()