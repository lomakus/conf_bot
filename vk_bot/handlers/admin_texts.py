from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import get_user_by_vk_id, set_text, get_text, get_all_texts
from vk_bot.handlers.states import user_states, clear_state
from vk_bot.handlers.rules import InTextEditingRule
from vk_bot.keyboards.main_menu import get_main_menu_keyboard


def register_handlers(bot: Bot):
    """Регистрирует хендлеры для управления текстами (для админов)."""

    # ============================================================
    # Кнопка "Изменить текст" — показывает инструкцию
    # ============================================================
    @bot.on.message(payload_contains={"action": "edit_text"})
    async def edit_text_instruction(msg: Message):
        """Показывает инструкцию по изменению текстов."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта функция доступна только админам.")
            return

        await msg.answer(
            "⚙️ УПРАВЛЕНИЕ ТЕКСТАМИ БОТА\n\n"
            "Доступны две команды:\n\n"
            "📋 /list_texts — посмотреть все ключи и описания\n\n"
            "✏️ /set_text <ключ> — изменить текст по ключу\n"
            "   Пример: /set_text faq_earn\n\n"
            "После ввода нового текста бот попросит подтверждение.\n"
            "Для отмены в любой момент напиши /cancel",
            keyboard=get_main_menu_keyboard(user['role'])
        )

    # ============================================================
    # Команда /list_texts — вывод всех ключей
    # ============================================================
    @bot.on.message(text="/list_texts")
    async def list_texts_handler(msg: Message):
        """Выводит список всех текстовых ключей."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта команда доступна только админам.")
            return

        texts = await get_all_texts()
        if not texts:
            await msg.answer("📋 Тексты не найдены.")
            return

        message = "📋 СПИСОК ТЕКСТОВЫХ КЛЮЧЕЙ\n\n"
        for text in texts:
            message += f"🔑 {text['key']}\n"
            message += f"   📝 {text['description'] or 'без описания'}\n"
            message += f"   🕐 Обновлено: {text['updated_at']}\n\n"

        await msg.answer(message, keyboard=get_main_menu_keyboard(user['role']))

    # ============================================================
    # Команда /set_text <key> — начало FSM
    # ============================================================
    @bot.on.message(text="/set_text <key>")
    async def start_set_text(msg: Message, key: str):
        """Начинает процесс изменения текста."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] != 'admin':
            await msg.answer("⛔ Эта команда доступна только админам.")
            return

        existing_text = await get_text(key)
        if not existing_text:
            await msg.answer(
                f"⚠️ Текст с ключом {key} не найден.\n\n"
                f"Используй /list_texts чтобы посмотреть все доступные ключи."
            )
            return

        user_states[msg.from_id] = {
            'type': 'text_editing',
            'step': 'awaiting_new_text',
            'data': {'key': key}
        }

        preview = existing_text[:300] + "..." if len(existing_text) > 300 else existing_text

        await msg.answer(
            f"✏️ ИЗМЕНЕНИЕ ТЕКСТА\n\n"
            f"🔑 Ключ: {key}\n\n"
            f"📄 Текущий текст:\n{preview}\n\n"
            f"Отправь НОВЫЙ ТЕКСТ одним сообщением.\n"
            f"Для отмены напиши /cancel"
        )

    # ============================================================
    # FSM для редактирования текста
    # ============================================================
    @bot.on.message(InTextEditingRule())
    async def text_editing_fsm(msg: Message):
        """FSM для ввода и подтверждения нового текста."""
        vk_id = msg.from_id
        state = user_states[vk_id]
        step = state['step']
        text = msg.text.strip() if msg.text else ""

        if msg.payload:
            return

        if text.startswith('/'):
            if text == '/cancel':
                clear_state(vk_id)
                user = await get_user_by_vk_id(vk_id)
                role = user['role'] if user else 'participant'
                await msg.answer(
                    "❌ Редактирование отменено.",
                    keyboard=get_main_menu_keyboard(role)
                )
                return
            else:
                await msg.answer("⚠️ Сначала заверши редактирование или напиши /cancel")
                return

        # --- ШАГ 1: Ввод нового текста ---
        if step == 'awaiting_new_text':
            if not text:
                await msg.answer("⚠️ Текст не может быть пустым. Отправь новый текст:")
                return

            state['data']['new_text'] = text
            state['step'] = 'awaiting_confirmation'
            preview = text[:300] + "..." if len(text) > 300 else text

            await msg.answer(
                f"✅ ПОДТВЕРЖДЕНИЕ ИЗМЕНЕНИЙ\n\n"
                f"🔑 Ключ: {state['data']['key']}\n\n"
                f"📄 Новый текст:\n{preview}\n\n"
                f"Напиши ДА для подтверждения или НЕТ для отмены.\n"
                f"Или просто отправь другой текст, чтобы переписать его."
            )
            return

        # --- ШАГ 2: Подтверждение ---
        if step == 'awaiting_confirmation':
            if text.lower() in ['да', 'yes', 'y', '+', 'подтверждаю', 'ок', 'ok']:
                key = state['data']['key']
                new_text = state['data']['new_text']

                success = await set_text(key, new_text)
                if success:
                    clear_state(vk_id)
                    user = await get_user_by_vk_id(vk_id)
                    role = user['role'] if user else 'participant'
                    await msg.answer(
                        f"✅ Текст {key} успешно обновлён!",
                        keyboard=get_main_menu_keyboard(role)
                    )
                    logger.info(f"Админ {vk_id} обновил текст '{key}'")
                else:
                    await msg.answer("❌ Ошибка при сохранении текста. Попробуй позже.")
                    clear_state(vk_id)
                return

            elif text.lower() in ['нет', 'no', 'n', '-', 'отмена', 'cancel']:
                clear_state(vk_id)
                user = await get_user_by_vk_id(vk_id)
                role = user['role'] if user else 'participant'
                await msg.answer(
                    "❌ Изменения отменены.",
                    keyboard=get_main_menu_keyboard(role)
                )
                return

            else:
                state['data']['new_text'] = text
                preview = text[:300] + "..." if len(text) > 300 else text

                await msg.answer(
                    f"🔄 НОВЫЙ ВАРИАНТ ТЕКСТА\n\n"
                    f"📄 Текст:\n{preview}\n\n"
                    f"Напиши ДА для подтверждения или НЕТ для отмены."
                )
                return

    # ============================================================
    # Команда /cancel — универсальная отмена
    # ============================================================
    @bot.on.message(text=["/cancel", "отмена"])
    async def cancel_handler(msg: Message):
        """Отменяет любой активный FSM."""
        vk_id = msg.from_id
        state = user_states.get(vk_id)

        if not state:
            return

        process_type = state.get('type')
        clear_state(vk_id)

        user = await get_user_by_vk_id(vk_id)
        role = user['role'] if user else 'participant'

        if process_type == 'registration':
            await msg.answer("❌ Регистрация отменена.", keyboard=get_main_menu_keyboard(role))
        elif process_type == 'award':
            await msg.answer("❌ Начисление жетонов отменено.", keyboard=get_main_menu_keyboard(role))
        elif process_type == 'text_editing':
            await msg.answer("❌ Редактирование текста отменено.", keyboard=get_main_menu_keyboard(role))
        elif process_type == 'broadcast':
            await msg.answer("❌ Рассылка отменена.", keyboard=get_main_menu_keyboard(role))
        else:
            await msg.answer("❌ Операция отменена.", keyboard=get_main_menu_keyboard(role))