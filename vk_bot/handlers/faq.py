from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import get_user_by_vk_id, get_text
from vk_bot.keyboards.main_menu import get_main_menu_keyboard, get_faq_keyboard


# Дефолтные тексты (на случай, если в БД пусто)
DEFAULT_FAQ_EARN = (
    "💰 Как заработать огоньки?\n\n"
    "1. Отправляй фото с выполненными заданиями\n"
    "2. Участвуй в активностях конференции\n"
    "3. Выполняй специальные задания\n\n"
    "💡 Чем активнее ты участвуешь, тем больше огоньков заработаешь!"
)

DEFAULT_FAQ_SPEND = (
    "🎁 На что тратить огоньки?\n\n"
    "1. Призы и подарки\n"
    "2. Привилегии\n"
    "3. Розыгрыши\n\n"
    "💡 Подробности узнай у служителей!"
)


def register_handlers(bot: Bot):
    """Регистрирует хендлеры раздела FAQ."""

    @bot.on.message(text=['faq', 'FAQ', 'Вопросы', 'вопросы', 'Ответы', 'ответы'])
    @bot.on.message(payload_contains={"action": "faq_menu"})
    async def faq_menu_handler(msg: Message):
        """Показывает меню вопросов и ответов."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        await msg.answer(
            "❓ Вопросы и ответы\n\n"
            "Выбери интересующий тебя вопрос:",
            keyboard=get_faq_keyboard()
        )

    @bot.on.message(payload_contains={"action": "faq_earn"})
    async def faq_earn_handler(msg: Message):
        """Отвечает на вопрос 'Как заработать огоньки?'."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        # Получаем текст из БД или используем дефолтный
        text = await get_text('faq_earn') or DEFAULT_FAQ_EARN

        await msg.answer(text, keyboard=get_faq_keyboard())

    @bot.on.message(payload_contains={"action": "faq_spend"})
    async def faq_spend_handler(msg: Message):
        """Отвечает на вопрос 'На что тратить огоньки?'."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        # Получаем текст из БД или используем дефолтный
        text = await get_text('faq_spend') or DEFAULT_FAQ_SPEND

        await msg.answer(text, keyboard=get_faq_keyboard())

    @bot.on.message(payload_contains={"action": "back_to_menu"})
    async def back_to_menu_handler(msg: Message):
        """Возвращает в главное меню."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        await msg.answer(
            "📋 Главное меню\n\nВыбери действие:",
            keyboard=get_main_menu_keyboard(user['role'])
        )