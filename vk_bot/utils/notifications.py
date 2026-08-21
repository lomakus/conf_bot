"""
Модуль для отправки уведомлений в специальный чат о важных событиях.
"""
from vkbottle import Bot
from vkbottle.modules import logger
from config import VK_NOTIFICATIONS_CHAT_ID
from database.queries import get_users_stats


async def send_notification(bot: Bot, message: str) -> None:
    """
    Отправляет уведомление в чат уведомлений.
    Не прерывает выполнение, если чат недоступен.
    """
    if not VK_NOTIFICATIONS_CHAT_ID:
        logger.warning("⚠️ VK_NOTIFICATIONS_CHAT_ID не настроен, уведомление не отправлено")
        return

    try:
        await bot.api.messages.send(
            peer_id=int(VK_NOTIFICATIONS_CHAT_ID),
            message=message,
            random_id=0,
        )
        logger.info(f"✅ Уведомление отправлено в чат {VK_NOTIFICATIONS_CHAT_ID}")
    except Exception as e:
        # Логируем, но не прерываем основную логику
        logger.error(f"❌ Ошибка отправки уведомления: {e}")


async def notify_new_registration(bot: Bot, user: dict) -> None:
    """Уведомление о новой регистрации со статистикой."""
    # Получаем статистику
    stats = await get_users_stats()

    message = (
        f"🆕 Новая регистрация #{user['id']}\n\n"
        f"👤 ФИО: {user['full_name']}\n"
        f"🆔 Никнейм: @{user['nickname']}\n"
        f"🎂 Возраст: {user['age']}\n"
        f"🏙️ Город: {user.get('city') or 'не указан'}\n"
        f"🎭 Роль: {user['role']}\n\n"
        f"📊 Статистика бота:\n"
        f"   👥 Всего: {stats['total']}\n"
        f"   🎫 Участников: {stats['participant']}\n"
        f"   🛡️ Служителей: {stats['staff']}\n"
        f"   👑 Админов: {stats['admin']}"
    )
    await send_notification(bot, message)


async def notify_score_change(
    bot: Bot,
    transaction_id: int,
    participant: dict,
    amount: int,
    tx_type: str,
    reason: str,
    staff: dict | None = None,
) -> None:
    """
    Уведомление о начислении или списании баллов.
    """
    emoji = "💰" if tx_type == "credit" else "💸"
    sign = "+" if tx_type == "credit" else "-"
    action = "Начисление" if tx_type == "credit" else "Списание"

    # Информация о служителе
    if staff:
        staff_info = f"{staff['role']} {staff['full_name']} ({staff['nickname']})"
    else:
        staff_info = "системой"

    message = (
        f"{emoji} {action} #{transaction_id}\n\n"
        f"👤 Участник: {participant['full_name']} ({participant['nickname']})\n"
        f"💰 Изменение: {sign}{amount} жетонов\n"
        f"📝 Причина: {reason}\n"
        f"🛡️ Кем выполнено: {staff_info}\n\n"
        f"📊 Текущий баланс: {participant['score']} жетонов"
    )
    await send_notification(bot, message)


async def notify_role_change(
    bot: Bot,
    user: dict,
    old_role: str,
    new_role: str,
) -> None:
    """Уведомление об изменении роли пользователя."""
    role_names = {
        'admin': '👑 Администратор',
        'staff': '🛡️ Служитель',
        'participant': '🎫 Участник'
    }

    old_role_display = role_names.get(old_role, old_role)
    new_role_display = role_names.get(new_role, new_role)

    message = (
        f"🔄 Изменение роли #{user['id']}\n\n"
        f"👤 ФИО: {user['full_name']}\n"
        f"🆔 Никнейм: {user['nickname']}\n\n"
        f"📋 Старая роль: {old_role_display}\n"
        f"📋 Новая роль: {new_role_display}"
    )
    await send_notification(bot, message)

async def notify_broadcast(
    bot: Bot,
    user: dict,
    role_name: str,
    success_count: int,
    error_count: int,
    count: int
) -> None:
    """Уведомление об изменении роли пользователя."""

    message = (
        f"✅ РАССЫЛКА ЗАВЕРШЕНА\n\n"
        f"👤 Отправитель: {user['full_name']} ({user['nickname']})\n"
        f"📋 Аудитория: {role_name}\n"
        f"✅ Успешно отправлено: {success_count}\n"
        f"❌ Ошибок: {error_count}\n"
        f"📊 Всего получателей: {count}",
    )
    await send_notification(bot, message)

async def notify_hearbeat(
    bot: Bot,
) -> None:
    """Уведомление об изменении роли пользователя."""

    message = (
        f"💓 Бот работает нормально\n🕐 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )
    await send_notification(bot, message)

async def notify_shutdown(
    bot: Bot,
) -> None:
    """Уведомление об остановке бота."""

    message = (
        f"🛑 Бот остановлен\n🕐 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )
    await send_notification(bot, message)