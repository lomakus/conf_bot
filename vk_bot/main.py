import asyncio
import logging
from vkbottle import Bot
from config import VK_BOT_TOKEN
from database.models import init_db
from vk_bot.utils.hearbeat import heartbeat_task
from vk_bot.utils.notifications import notify_shutdown


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    """Главная функция запуска бота."""
    # 1. Инициализация БД
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("✅ База данных готова")

    # 2. Создание бота
    if not VK_BOT_TOKEN:
        logger.error("❌ VK_BOT_TOKEN не найден в .env!")
        return

    bot = Bot(token=VK_BOT_TOKEN)

    # 3. Регистрация хендлеров (добавим в следующих этапах)
    from vk_bot.handlers import registration, profile, start, role, submission, award, faq, shop, admin_texts, broadcast, admin_analytics
    start.register_start_handlers(bot)
    submission.register_phot_handlers(bot)
    profile.register_profile_handlers(bot)
    role.register_role_handlers(bot)
    faq.register_handlers(bot)
    shop.register_handlers(bot)
    admin_analytics.register_handlers(bot)
    admin_texts.register_handlers(bot)
    award.register_award_handlers(bot)
    registration.register_handlers(bot)
    broadcast.register_handlers(bot)

    # Запускаем heartbeat как фоновую задачу
    heartbeat = asyncio.create_task(heartbeat_task(bot, interval_seconds=60))

    logger.info("🚀 VK-бот запущен!")

    # 4. Запуск polling
    await bot.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")