from vkbottle import Keyboard, KeyboardButtonColor, Text

def get_register_keyboard() -> str:
    """Клавиатура с кнопкой регистрации."""
    kb = Keyboard(one_time=True)
    kb.add(Text("📝 Зарегистрироваться", payload={"action": "register"}), color=KeyboardButtonColor.POSITIVE)
    kb.add(Text("📝 Войти", payload={"action": "login"}), color=KeyboardButtonColor.PRIMARY)

    return kb

def get_main_menu_keyboard(role: str = 'participant') -> str:
    """Возвращает JSON главной клавиатуры."""
    kb = Keyboard(one_time=True)

    kb.add(Text("👤 Мой профиль", payload={"action": "profile"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("📜 История баллов", payload={"action": "history"}), color=KeyboardButtonColor.SECONDARY)
    # kb.add(Text("🏆 Рейтинг"), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("📸 Отправить фото", payload={"action": "submit_photo"}), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text("🛒 Магазин", payload={"action": "shop"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("❓ Вопросы и ответы", payload={"action": "faq_menu"}), color=KeyboardButtonColor.SECONDARY)

    # Кнопка только для служителей и админов
    if role in ('staff', 'admin'):
        kb.row()
        kb.add(Text("💰 Начислить/списать жетоны", payload={"action": "award_tokens"}), color=KeyboardButtonColor.PRIMARY)

    # Кнопка только для админов
    if role == 'admin':
        kb.add(Text("⚙️ Изменить текст", payload={"action": "edit_text"}), color=KeyboardButtonColor.NEGATIVE)
        kb.row()
        kb.add(Text("📢 Общее сообщение", payload={"action": "broadcast_menu"}), color=KeyboardButtonColor.NEGATIVE)
        kb.add(Text("📊 Статистика", payload={"action": "admin_stats"}), color=KeyboardButtonColor.NEGATIVE)
        kb.row()
        kb.add(Text("🏆 Топ рейтинг", payload={"action": "admin_rating"}), color=KeyboardButtonColor.NEGATIVE)
        kb.add(Text("📜 История транзакций", payload={"action": "admin_transactions"}), color=KeyboardButtonColor.NEGATIVE)


    return kb


def get_faq_keyboard() -> str:
    """Клавиатура с вопросами FAQ."""
    kb = Keyboard(one_time=True)

    kb.add(Text("💰 Как заработать жетоны?", payload={"action": "faq_earn"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("🎁 На что тратить жетоны?", payload={"action": "faq_spend"}), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("🔙 Назад в меню", payload={"action": "back_to_menu"}), color=KeyboardButtonColor.SECONDARY)

    return kb


def get_broadcast_audience_keyboard() -> str:
    """Клавиатура выбора аудитории для рассылки."""
    kb = Keyboard(one_time=True)

    kb.add(Text("🎫 Участникам", payload={"action": "broadcast_participants"}), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("🛡️ Служителям", payload={"action": "broadcast_staff"}), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("🔙 Назад", payload={"action": "back_to_menu"}), color=KeyboardButtonColor.SECONDARY)

    return kb