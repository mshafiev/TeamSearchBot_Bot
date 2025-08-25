import os
from dotenv import load_dotenv

load_dotenv()

# Настройки рассылки уведомлений
NOTIFICATION_INTERVAL_DAYS = int(os.getenv("NOTIFICATION_INTERVAL_DAYS", "5"))
NOTIFICATION_DELAY_BETWEEN_MESSAGES = float(os.getenv("NOTIFICATION_DELAY_BETWEEN_MESSAGES", "0.1"))

# Настройки администраторов
ADMIN_IDS = os.getenv("ADMIN_IDS", "1008114047").split(",")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
