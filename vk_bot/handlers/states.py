# vk_bot/handlers/states.py

"""
Общее состояние пользователей для FSM.
Вынесено в отдельный файл, чтобы избежать circular import.
"""

# Словарь для хранения состояний пользователей
# Структура: { vk_id: {"step": str, "data": dict} }
user_states = {}


def clear_state(vk_id: int):
    """Очищает состояние пользователя."""
    if vk_id in user_states:
        del user_states[vk_id]