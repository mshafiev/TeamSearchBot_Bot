import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from aiogram import Bot
from api_client import APIClient
import app.texts as texts
import app.config as config

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Планировщик для автоматической рассылки уведомлений"""
    
    def __init__(self, bot: Bot, api_client: APIClient):
        self.bot = bot
        self.api_client = api_client
        self.is_running = False
        self.task = None
    
    async def start(self):
        """Запустить планировщик"""
        if self.is_running:
            logger.warning("Планировщик уже запущен")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info(f"Планировщик уведомлений запущен (интервал: {config.NOTIFICATION_INTERVAL_DAYS} дней)")
    
    async def stop(self):
        """Остановить планировщик"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Планировщик уведомлений остановлен")
    
    async def _run_scheduler(self):
        """Основной цикл планировщика"""
        while self.is_running:
            try:
                # Ждем до следующего запуска (каждые N дней)
                interval_seconds = config.NOTIFICATION_INTERVAL_DAYS * 24 * 60 * 60
                logger.info(f"Следующая рассылка через {config.NOTIFICATION_INTERVAL_DAYS} дней")
                await asyncio.sleep(interval_seconds)
                
                if self.is_running:
                    await self._send_notifications_to_all_users()
                    
            except asyncio.CancelledError:
                logger.info("Планировщик уведомлений остановлен")
                break
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                # Ждем час перед повторной попыткой
                await asyncio.sleep(60 * 60)
    
    async def _send_notifications_to_all_users(self):
        """Отправить уведомления всем пользователям"""
        try:
            logger.info("Начинаю рассылку уведомлений о новых анкетах")
            
            # Получаем всех пользователей
            users = self.api_client.get_all_users()
            
            if not users:
                logger.warning("Не удалось получить список пользователей")
                return
            
            logger.info(f"Найдено {len(users)} пользователей для рассылки")
            
            # Отправляем уведомления
            success_count = 0
            error_count = 0
            
            for user in users:
                try:
                    tg_id = user.get('tg_id')
                    if not tg_id:
                        continue
                    
                    # Отправляем уведомление
                    await self.bot.send_message(
                        chat_id=tg_id,
                        text=texts.NEW_PROFILES_NOTIFICATION
                    )
                    
                    success_count += 1
                    
                    # Небольшая задержка между сообщениями, чтобы не перегружать API
                    await asyncio.sleep(config.NOTIFICATION_DELAY_BETWEEN_MESSAGES)
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Ошибка отправки уведомления пользователю {user.get('tg_id', 'unknown')}: {e}")
            
            logger.info(f"Рассылка завершена. Успешно: {success_count}, ошибок: {error_count}")
            
        except Exception as e:
            logger.error(f"Ошибка при рассылке уведомлений: {e}")
    
    async def send_test_notification(self, test_user_id: str):
        """Отправить тестовое уведомление (для проверки)"""
        try:
            await self.bot.send_message(
                chat_id=test_user_id,
                text=texts.NEW_PROFILES_NOTIFICATION
            )
            logger.info(f"Тестовое уведомление отправлено пользователю {test_user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки тестового уведомления: {e}")
    
    async def force_send_notifications(self):
        """Принудительно отправить уведомления (не дожидаясь N дней)"""
        logger.info("Принудительная отправка уведомлений")
        await self._send_notifications_to_all_users()
