from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import get_user_by_vk_id, get_users_by_role
from vk_bot.handlers.states import user_states, clear_state
from vk_bot.handlers.rules import InBroadcastingRule
from vk_bot.keyboards.main_menu import get_main_menu_keyboard, get_broadcast_audience_keyboard
from vk_bot.utils.notifications import notify_broadcast

# Маппинг ролей
ROLE_MAP = {
    'broadcast_participants': 'participant',
    'broadcast_staff': 'staff',
}

ROLE_NAMES = {
    'participant': 'участникам',
    'staff': 'служителям',
}


def register_handlers(bot: Bot):
    """Регистрирует хендлеры массовой рассылки."""

    # ============================================================
    # Кнопка "Общее сообщение" — показывает выбор аудитории
    # ============================================================
    @bot.on.message(payload_contains={"action": "broadcast_menu"})
    async def broadcast_menu_handler(msg: Message):
        """Показывает меню выбора аудитории для рассылки."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта функция доступна только админам.")
            return

        await msg.answer(
            "📢 МАССОВАЯ РАССЫЛКА\n\n"
            "Выбери, кому отправить сообщение:",
            keyboard=get_broadcast_audience_keyboard()
        )

    # ============================================================
    # Выбор аудитории — начало FSM
    # ============================================================
    @bot.on.message(payload_contains={"action": "broadcast_participants"})
    @bot.on.message(payload_contains={"action": "broadcast_staff"})
    async def broadcast_select_audience(msg: Message):
        """Начинает процесс рассылки после выбора аудитории."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта функция доступна только админам.")
            return

        # Определяем роль из payload
        import json
        payload = json.loads(msg.payload)
        action = payload.get('action')
        target_role = ROLE_MAP.get(action)

        if not target_role:
            await msg.answer("⚠️ Неизвестная аудитория.")
            return

        # Инициализируем состояние
        user_states[msg.from_id] = {
            'type': 'broadcast',
            'step': 'awaiting_message',
            'data': {'target_role': target_role}
        }

        role_name = ROLE_NAMES[target_role]

        await msg.answer(
            f"📢 РАССЫЛКА {role_name.upper()}\n\n"
            f"Отправь текстовое сообщение, которое будет разослано всем {role_name}.\n\n"
            f"Для отмены напиши /cancel"
        )

    # ============================================================
    # FSM для рассылки
    # ============================================================
    @bot.on.message(InBroadcastingRule())
    async def broadcast_fsm(msg: Message):
        """FSM для ввода и подтверждения сообщения для рассылки."""
        vk_id = msg.from_id
        state = user_states[vk_id]
        step = state['step']
        text = msg.text.strip() if msg.text else ""

        # Игнорируем payload во время FSM
        if msg.payload:
            return

        # Обработка команды /cancel
        if text.startswith('/'):
            if text == '/cancel':
                clear_state(vk_id)
                user = await get_user_by_vk_id(vk_id)
                role = user['role'] if user else 'participant'
                await msg.answer(
                    "❌ Рассылка отменена.",
                    keyboard=get_main_menu_keyboard(role)
                )
                return
            else:
                await msg.answer("⚠️ Сначала заверши рассылку или напиши /cancel")
                return

        target_role = state['data']['target_role']
        role_name = ROLE_NAMES[target_role]

        # --- ШАГ 1: Ввод сообщения ---
        if step == 'awaiting_message':
            if not text:
                await msg.answer("⚠️ Сообщение не может быть пустым. Отправь текст:")
                return

            # Сохраняем сообщение
            state['data']['message'] = text
            state['step'] = 'awaiting_confirmation'

            # Показываем превью
            preview = text[:300] + "..." if len(text) > 300 else text

            await msg.answer(
                f"✅ ПОДТВЕРЖДЕНИЕ РАССЫЛКИ\n\n"
                f"📋 Аудитория: {role_name}\n\n"
                f"📄 Сообщение:\n{preview}\n\n"
                f"Напиши ДА для подтверждения или НЕТ для отмены.\n"
                f"Или отправь другое сообщение, чтобы изменить его."
            )
            return

        # --- ШАГ 2: Подтверждение ---
        if step == 'awaiting_confirmation':
            if text.lower() in ['да', 'yes', 'y', '+', 'подтверждаю', 'ок', 'ok']:
                # Выполняем рассылку
                message_text = state['data']['message']

                # Получаем список получателей
                recipients = await get_users_by_role(target_role)

                if not recipients:
                    clear_state(vk_id)
                    user = await get_user_by_vk_id(vk_id)
                    role = user['role'] if user else 'participant'
                    await msg.answer(
                        f"⚠️ Нет пользователей с ролью {role_name}.",
                        keyboard=get_main_menu_keyboard(role)
                    )
                    return

                # Рассылаем сообщения
                success_count = 0
                error_count = 0

                for recipient in recipients:
                    try:
                        await bot.api.messages.send(
                            user_id=recipient['vk_id'],
                            message=message_text,
                            random_id=0,
                        )
                        success_count += 1
                    except Exception as e:
                        logger.warning(f"Не удалось отправить сообщение пользователю {recipient['vk_id']}: {e}")
                        error_count += 1

                # Очищаем состояние
                clear_state(vk_id)
                user = await get_user_by_vk_id(vk_id)
                role = user['role'] if user else 'participant'
                count_rec = len(recipients)

                await notify_broadcast(bot, user, role_name, success_count, error_count, count_rec)

                # Отправляем отчёт админу
                await msg.answer(
                    f"✅ РАССЫЛКА ЗАВЕРШЕНА\n\n"
                    f"📋 Аудитория: {role_name}\n"
                    f"✅ Успешно отправлено: {success_count}\n"
                    f"❌ Ошибок: {error_count}\n"
                    f"📊 Всего получателей: {count_rec}",
                    keyboard=get_main_menu_keyboard(role)
                )

                logger.info(
                    f"Админ {vk_id} выполнил рассылку {role_name}: {success_count} успешно, {error_count} ошибок")
                return

            elif text.lower() in ['нет', 'no', 'n', '-', 'отмена', 'cancel']:
                clear_state(vk_id)
                user = await get_user_by_vk_id(vk_id)
                role = user['role'] if user else 'participant'
                await msg.answer(
                    "❌ Рассылка отменена.",
                    keyboard=get_main_menu_keyboard(role)
                )
                return

            else:
                # Если отправил другой текст — считаем это новым вариантом
                state['data']['message'] = text
                preview = text[:300] + "..." if len(text) > 300 else text

                await msg.answer(
                    f"🔄 НОВЫЙ ВАРИАНТ СООБЩЕНИЯ\n\n"
                    f"📄 Текст:\n{preview}\n\n"
                    f"Напиши ДА для подтверждения или НЕТ для отмены."
                )
                return