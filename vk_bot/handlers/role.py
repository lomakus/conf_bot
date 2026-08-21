from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import get_user_by_vk_id, update_role
from vk_bot.utils.notifications import notify_role_change


def register_role_handlers(bot: Bot):
    """Регистрирует хендлеры смены роли для самого пользователя."""

    @bot.on.message(text="/role_participant")
    async def role_participant(msg: Message):
        """Сделать себя участником."""
        await set_role(msg, "participant", "🎫 Участник")

    @bot.on.message(text="/role_staff")
    async def role_staff(msg: Message):
        """Сделать себя служителем."""
        await set_role(msg, "staff", "🛡️ Служитель")

    @bot.on.message(text="/role_admin")
    async def role_admin(msg: Message):
        """Сделать себя админом."""
        await set_role(msg, "admin", "👑 Администратор")

    async def set_role(msg: Message, new_role: str, role_display: str):
        """Общая логика смены роли."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        if user['role'] == new_role:
            await msg.answer(f"ℹ️ У тебя уже роль {role_display}.")
            return

        old_role = user['role']
        success = await update_role(user['id'], new_role)
        if success:
            await msg.answer(f"✅ Твоя новая роль: {role_display}")
            logger.info(f"Пользователь {user['nickname']} сменил роль на {new_role}")

            await notify_role_change(bot, user, old_role, new_role)
        else:
            await msg.answer("❌ Ошибка при смене роли.")