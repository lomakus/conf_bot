import asyncio
import logging
from vkbottle import Bot
from config import VK_NOTIFICATIONS_CHAT_ID
from vk_bot.utils.notifications import notify_hearbeat

logger = logging.getLogger(__name__)


async def heartbeat_task(bot: Bot, interval_seconds: int = 60):
    """
    Периодическая задача, которая логирует состояние бота.

    :param bot: Экземпляр бота
    :param interval_seconds: Интервал в секундах (по умолчанию 60)
    """
    logger.info(f"✅ Heartbeat запущен (интервал: {interval_seconds} сек)")

    while True:
        try:
            # Ждём интервал
            await asyncio.sleep(interval_seconds)

            # Логируем в консоль
            logger.info(f"💓 Бот работает нормально (heartbeat)")

            await notify_hearbeat(bot)

        except asyncio.CancelledError:
            logger.info("Heartbeat остановлен")
            break
        except Exception as e:
            logger.error(f"Ошибка в heartbeat: {e}")
            # Продолжаем работать, даже если была ошибка
            await asyncio.sleep(interval_seconds)