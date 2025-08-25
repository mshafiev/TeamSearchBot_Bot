#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы уведомлений
"""

import asyncio
import logging
from dotenv import load_dotenv
from app.scheduler import NotificationScheduler
from api_client import APIClient
from aiogram import Bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_notification_system():
    """Тестирование системы уведомлений"""
    load_dotenv()
    
    # Получаем токен бота
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ Ошибка: не найден BOT_TOKEN в .env файле")
        return
    
    # Создаем экземпляры
    bot = Bot(token=bot_token)
    client = APIClient()
    scheduler = NotificationScheduler(bot, client)
    
    try:
        print("🧪 Тестирование системы уведомлений...")
        
        # Тест 1: Получение пользователей
        print("\n1️⃣ Тест получения пользователей...")
        try:
            users = client.get_all_users()
            print(f"✅ Получено {len(users)} пользователей")
        except Exception as e:
            print(f"❌ Ошибка получения пользователей: {e}")
            return
        
        # Тест 2: Отправка тестового уведомления
        print("\n2️⃣ Тест отправки уведомления...")
        if users:
            test_user_id = users[0].get('tg_id')
            if test_user_id:
                try:
                    await scheduler.send_test_notification(test_user_id)
                    print(f"✅ Тестовое уведомление отправлено пользователю {test_user_id}")
                except Exception as e:
                    print(f"❌ Ошибка отправки тестового уведомления: {e}")
            else:
                print("⚠️ Не удалось получить test_user_id")
        
        # Тест 3: Проверка планировщика
        print("\n3️⃣ Тест планировщика...")
        try:
            await scheduler.start()
            print("✅ Планировщик запущен")
            
            # Ждем немного
            await asyncio.sleep(2)
            
            await scheduler.stop()
            print("✅ Планировщик остановлен")
        except Exception as e:
            print(f"❌ Ошибка работы планировщика: {e}")
        
        print("\n🎉 Все тесты завершены!")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
    
    finally:
        # Закрываем бота
        await bot.session.close()

if __name__ == "__main__":
    import os
    asyncio.run(test_notification_system())
