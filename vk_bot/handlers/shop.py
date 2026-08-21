from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import get_user_by_vk_id, get_text
from vk_bot.keyboards.main_menu import get_main_menu_keyboard


# Дефолтный текст на случай, если в БД пусто
DEFAULT_SHOP_TEXT = (
    "🛒 МАГАЗИН\n\n"
    "Список товаров временно недоступен.\n"
    "Обратись к служителю для получения информации."
)


def register_handlers(bot: Bot):
    """Регистрирует хендлеры магазина."""

    @bot.on.message(text=['Shop', 'shop', 'Магазин', 'магазин'])
    @bot.on.message(payload_contains={"action": "shop"})
    async def shop_handler(msg: Message):
        """Показывает список товаров."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        # Получаем текст из БД или используем дефолтный
        shop_text = await get_text('shop') or DEFAULT_SHOP_TEXT

        await msg.answer(
            shop_text,
            keyboard=get_main_menu_keyboard(user['role'])
        )