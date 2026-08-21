from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import (
    get_user_by_vk_id,
    get_users_stats,
    get_top_users,
    get_recent_transactions,
)
from vk_bot.keyboards.main_menu import get_main_menu_keyboard


def register_handlers(bot: Bot):
    """Регистрирует хендлеры админской аналитики."""

    # ============================================================
    # Статистика пользователей
    # ============================================================
    @bot.on.message(payload_contains={"action": "admin_stats"})
    async def admin_stats_handler(msg: Message):
        """Показывает статистику по пользователям."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта функция доступна только админам.")
            return

        stats = await get_users_stats()

        message = (
            "📊 СТАТИСТИКА БОТА\n\n"
            f"👥 Всего пользователей: {stats['total']}\n\n"
            f"🎫 Участников: {stats['participant']}\n"
            f"🛡️ Служителей: {stats['staff']}\n"
            f"👑 Админов: {stats['admin']}\n\n"
            f"📈 Распределение ролей:\n"
        )

        if stats['total'] > 0:
            participant_pct = (stats['participant'] / stats['total']) * 100
            staff_pct = (stats['staff'] / stats['total']) * 100
            admin_pct = (stats['admin'] / stats['total']) * 100

            message += f"   • Участники: {participant_pct:.1f}%\n"
            message += f"   • Служители: {staff_pct:.1f}%\n"
            message += f"   • Админы: {admin_pct:.1f}%"

        await msg.answer(message, keyboard=get_main_menu_keyboard(user['role']))

    # ============================================================
    # Топ рейтинг
    # ============================================================
    @bot.on.message(payload_contains={"action": "admin_rating"})
    async def admin_rating_handler(msg: Message):
        """Показывает топ 20 пользователей по балансу."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта функция доступна только админам.")
            return

        top_users = await get_top_users(limit=20)

        if not top_users:
            await msg.answer("📊 Пока нет зарегистрированных пользователей.")
            return

        message = "🏆 ТОП 20 ПО ЖЕТОНАМ\n\n"

        for i, u in enumerate(top_users, 1):
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "

            message += f"{medal}{i}. @{u['nickname']}\n"
            message += f"   👤 {u['full_name']}\n"
            message += f"   💰 {u['score']} жетонов\n"
            message += f"   🎭 {u['role']}\n\n"

        await msg.answer(message, keyboard=get_main_menu_keyboard(user['role']))

    # ============================================================
    # История транзакций
    # ============================================================
    @bot.on.message(payload_contains={"action": "admin_transactions"})
    async def admin_transactions_handler(msg: Message):
        """Показывает последние 30 транзакций."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта функция доступна только админам.")
            return

        transactions = await get_recent_transactions(limit=30)

        if not transactions:
            await msg.answer("📜 Пока нет транзакций.")
            return

        message = "📜 ПОСЛЕДНИЕ 30 ТРАНЗАКЦИЙ\n\n"

        for tx in transactions:
            emoji = "💰" if tx['type'] == 'credit' else "💸"
            sign = "+" if tx['type'] == 'credit' else "-"

            message += f"{emoji} #{tx['id']}\n"
            message += f"   👤 @{tx['user_nickname']} ({tx['user_name']})\n"
            message += f"   💰 {sign}{tx['amount']} жетонов\n"

            if tx['description']:
                message += f"   📝 {tx['description']}\n"

            if tx['creator_name']:
                message += f"   🛡️ {tx['creator_name']} (@{tx['creator_nickname']})\n"

            message += f"   🕐 {tx['created_at']}\n\n"

        await msg.answer(message, keyboard=get_main_menu_keyboard(user['role']))