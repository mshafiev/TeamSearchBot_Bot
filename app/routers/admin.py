from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging
from api_client import APIClient
import app.texts as texts
import app.config as config
import asyncio

logger = logging.getLogger(__name__)

router = Router()

def is_admin(user_id: str) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return user_id in config.ADMIN_IDS

@router.message(Command("admin"))
async def admin_menu(message: Message):
    """Показать меню администратора"""
    if not is_admin(str(message.from_user.id)):
        await message.answer("У вас нет доступа к административным функциям.")
        return
    
    admin_text = (
        "🔧 Административное меню:\n\n"
        "📢 /send_notifications - Отправить уведомления всем пользователям\n"
        "🧪 /test_notification <user_id> - Отправить тестовое уведомление\n"
        "📊 /stats - Статистика пользователей\n"
        "❓ /help_admin - Справка по командам"
    )
    
    await message.answer(admin_text)

@router.message(Command("send_notifications"))
async def force_send_notifications(message: Message):
    """Принудительно отправить уведомления всем пользователям"""
    if not is_admin(str(message.from_user.id)):
        await message.answer("У вас нет доступа к административным функциям.")
        return
    
    try:
        await message.answer("🔄 Начинаю рассылку уведомлений...")
        
        # Получаем всех пользователей
        client = APIClient()  # Используем настройки по умолчанию
        users = client.get_all_users()
        
        if not users:
            await message.answer("❌ Не удалось получить список пользователей")
            return
        
        # Отправляем уведомления
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                tg_id = user.get('tg_id')
                if not tg_id:
                    continue
                
                # Отправляем уведомление
                await message.bot.send_message(
                    chat_id=tg_id,
                    text=texts.NEW_PROFILES_NOTIFICATION
                )
                
                success_count += 1
                
                # Небольшая задержка между сообщениями
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Ошибка отправки уведомления пользователю {user.get('tg_id', 'unknown')}: {e}")
        
        result_text = (
            f"✅ Рассылка завершена!\n\n"
            f"📊 Статистика:\n"
            f"• Успешно отправлено: {success_count}\n"
            f"• Ошибок: {error_count}\n"
            f"• Всего пользователей: {len(users)}"
        )
        
        await message.answer(result_text)
        
    except Exception as e:
        logger.error(f"Ошибка при принудительной рассылке: {e}")
        await message.answer(f"❌ Ошибка при рассылке: {e}")

@router.message(Command("test_notification"))
async def test_notification(message: Message):
    """Отправить тестовое уведомление указанному пользователю"""
    if not is_admin(str(message.from_user.id)):
        await message.answer("У вас нет доступа к административным функциям.")
        return
    
    # Парсим команду: /test_notification <user_id>
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.answer("❌ Использование: /test_notification <user_id>")
        return
    
    user_id = command_parts[1]
    
    try:
        await message.bot.send_message(
            chat_id=user_id,
            text=texts.NEW_PROFILES_NOTIFICATION
        )
        await message.answer(f"✅ Тестовое уведомление отправлено пользователю {user_id}")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки тестового уведомления: {e}")

@router.message(Command("stats"))
async def show_stats(message: Message):
    """Показать статистику пользователей"""
    if not is_admin(str(message.from_user.id)):
        await message.answer("У вас нет доступа к административным функциям.")
        return
    
    try:
        client = APIClient()
        users = client.get_all_users()
        
        if not users:
            await message.answer("❌ Не удалось получить статистику")
            return
        
        stats_text = (
            f"📊 Статистика пользователей:\n\n"
            f"👥 Всего пользователей: {len(users)}\n"
            f"📅 Последнее обновление: {message.date.strftime('%d.%m.%Y %H:%M')}"
        )
        
        await message.answer(stats_text)
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await message.answer(f"❌ Ошибка при получении статистики: {e}")

@router.message(Command("help_admin"))
async def admin_help(message: Message):
    """Показать справку по административным командам"""
    if not is_admin(str(message.from_user.id)):
        await message.answer("У вас нет доступа к административным функциям.")
        return
    
    help_text = (
        "📚 Справка по административным командам:\n\n"
        "🔧 /admin - Главное меню администратора\n"
        "📢 /send_notifications - Принудительно отправить уведомления всем пользователям\n"
        "🧪 /test_notification <user_id> - Отправить тестовое уведомление конкретному пользователю\n"
        "📊 /stats - Показать статистику пользователей\n"
        "❓ /help_admin - Эта справка\n\n"
        f"💡 Автоматическая рассылка происходит каждые {config.NOTIFICATION_INTERVAL_DAYS} дней\n"
        f"⚙️ Интервал настраивается через переменную NOTIFICATION_INTERVAL_DAYS"
    )
    
    await message.answer(help_text)
