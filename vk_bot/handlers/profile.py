from vkbottle.bot import Bot, Message
from database.queries import (
    get_user_by_vk_id,
    get_user_score,
    get_user_transactions
)
from vk_bot.keyboards.main_menu import get_main_menu_keyboard
import logging

logger = logging.getLogger(__name__)


def register_profile_handlers(bot: Bot):
    """Регистрирует хендлеры профиля и истории."""

    @bot.on.message(text=['Профиль', 'профиль'])
    @bot.on.message(payload_contains={"action": "profile"})
    async def profile_handler(msg: Message):
        """Показывает профиль пользователя с балансом."""

        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        score = await get_user_score(user['id'])

        # Красивое отображение роли
        role_names = {
            'admin': '👑 Администратор',
            'staff': '🛡️ Служитель',
            'participant': '🎫 Участник'
        }
        role_display = role_names.get(user['role'], user['role'])

        profile_text = (
            f"👤 Твой профиль\n\n"
            f"📛 ФИО: {user['full_name']}\n"
            f"🆔 Никнейм: {user['nickname']}\n"
            f"🎂 Возраст: {user['age']} лет\n"
            f"🏙️ Город: {user['city'] or 'не указан'}\n"
            f"🎭 Роль: {role_display}\n\n"
            f"💰 Баланс: {score} баллов"
        )

        await msg.answer(profile_text, keyboard=get_main_menu_keyboard(user['role']))

    @bot.on.message(text=['История', 'история'])
    @bot.on.message(payload_contains={"action": "history"})
    async def history_handler(msg: Message):
        """Показывает историю начислений и списаний."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        transactions = await get_user_transactions(user['id'], limit=20)

        if not transactions:
            await msg.answer(
                "📜 История баллов\n\n"
                "У тебя пока нет транзакций.\n"
                "Баллы начисляются за выполнение заданий!",
                keyboard=get_main_menu_keyboard(user['role'])
            )
            return

        # Формируем текст истории
        history_text = "📜 История баллов (последние 20 операций)\n\n"

        for tx in transactions:
            # Определяем знак и эмодзи
            if tx['type'] == 'credit':
                sign = "+"
                emoji = "✅"
            else:
                sign = "-"
                emoji = "❌"

            # Кто начислил/снял
            if tx['created_by_name']:
                by_info = f"от {tx['created_by_name']}"
            else:
                by_info = "системой"

            # Дата (обрезаем время для краткости)
            date = tx['created_at'].split(' ')[0] if tx['created_at'] else 'неизвестно'

            history_text += (
                f"{emoji} {sign}{tx['amount']} баллов\n"
                f"   📝 {tx['description'] or 'без описания'}\n"
                f"   👤 {by_info}\n"
                f"   📅 {date}\n\n"
            )

        await msg.answer(history_text, keyboard=get_main_menu_keyboard(user['role']))

    # @bot.on.message()
    # async def catch_all_handler(msg: Message):
    #     """Ловит ВСЕ сообщения, которые не поймали другие хендлеры."""
    #     logger.info(f"DEBUG: Перехвачено сообщение. Текст: '{msg.text}', Payload: '{msg.payload}'")