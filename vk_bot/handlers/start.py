from vkbottle.bot import Bot, Message
import logging
from database.queries import (
    get_user_by_vk_id
)
from vk_bot.keyboards.main_menu import get_main_menu_keyboard, get_register_keyboard
from database.queries import get_text

logger = logging.getLogger(__name__)

import time
def register_start_handlers(bot: Bot):
    """Регистрирует хендлеры регистрации."""

    # @bot.on.message(text=["/start", "начать", "старт", "Начать", "Старт", "Привет", "привет"])
    # async def start_time_handler(msg: Message):
    #     """Проверка при старте: зарегистрирован ли уже пользователь."""
    #
    #     # Засекаем общее время начала
    #     total_start = time.time()
    #     logger.info(f"⏱️ [START] Получено сообщение от {msg.from_id}")
    #
    #     # Замер времени запроса к БД
    #     db_start = time.time()
    #     user = await get_user_by_vk_id(msg.from_id)
    #     db_time = time.time() - db_start
    #     logger.info(f"⏱️ [DB] Запрос к базе данных занял: {db_time:.3f} сек")
    #
    #     # Замер времени отправки ответа в VK
    #     api_start = time.time()
    #     if user:
    #         await msg.answer(
    #             f"Привет, {user['full_name']}! Ты уже зарегистрирован.",
    #             keyboard=get_main_menu_keyboard()
    #         )
    #     else:
    #         await msg.answer(
    #             "👋 Привет! Я бот конференции.\n\n"
    #             "Для взаимодействия необходимо зарегистрироваться или войти.\n"
    #             "Нажми на кнопку ниже, чтобы начать.",
    #             keyboard=get_register_keyboard()
    #         )
    #     api_time = time.time() - api_start
    #     logger.info(f"⏱️ [API] Отправка ответа в VK заняла: {api_time:.3f} сек")
    #
    #     # Общее время
    #     total_time = time.time() - total_start
    #     logger.info(f"⏱️ [TOTAL] Общее время обработки: {total_time:.3f} сек")

    @bot.on.message(text=["/start", "начать", "старт", "Начать", "Старт", "Привет", "привет", "Меню", "меню"])
    # @bot.on.message()
    async def start_handler(msg: Message):
        """Проверка при старте: зарегистрирован ли уже пользователь."""
        user = await get_user_by_vk_id(msg.from_id)
        if user:
            await msg.answer(
                f"👋 Привет, {user['full_name']}!\n\n"
                f"Ты находишься в главном меню.\n\n"
                f"📋 ДОСТУПНЫЕ ДЕЙСТВИЯ:\n"
                f"• 👤 Профиль — посмотреть свои данные\n"
                f"• 📜 История — история начислений и трат\n"
                f"• 📸 Фото — отправить фото на проверку\n"
                f"• 🛒 Магазин — обменять жетоны на товары\n"
                f"• ❓ Вопросы и ответы — полезная информация\n\n"
                f"💡 Если кнопки не появились, ты можешь написать текстом:\n"
                f"Профиль, История, Фото, Магазин, Вопросы",
                keyboard=get_main_menu_keyboard(user['role'])
            )
        else:
            welcome_message_text = await get_text('welcome_message')
            await msg.answer(
                welcome_message_text,
                keyboard=get_register_keyboard()
            )

    # @bot.on.message()
    # async def catch_all_handler(msg: Message):
    #     """Ловит ВСЕ сообщения, которые не поймали другие хендлеры."""
    #     logger.info(f"DEBUG: Перехвачено сообщение. Текст: '{msg.text}', Payload: '{msg.payload}'")

# import asyncio
#
# from vkbottle.bot import Bot, Message
# from vkbottle.modules import logger
#
#
# def register_handlers(bot: Bot):
#     """Регистрирует хендлеры регистрации."""
#
#     @bot.on.message(text="/start1")
#     async def start_handler(msg: Message):
#         """Обработчик команды /start."""
#         await asyncio.sleep(1)
#         await msg.answer("Привет! Я бот конференции. Напиши /register для регистрации.")
#         logger.info(f"Пользователь {msg.from_id} запустил бота")
#
#     @bot.on.message(text="/start2")
#     async def start_handler(msg: Message):
#         """Обработчик команды /start."""
#         await asyncio.sleep(2)
#         await msg.answer("Привет! Я бот конференции. Напиши /register для регистрации.")
#         logger.info(f"Пользователь {msg.from_id} запустил бота")
#
#     @bot.on.message(text="/start3")
#     async def start_handler(msg: Message):
#         """Обработчик команды /start."""
#         await asyncio.sleep(3)
#         await msg.answer("Привет! Я бот конференции. Напиши /register для регистрации.")
#         logger.info(f"Пользователь {msg.from_id} запустил бота")
#
#
