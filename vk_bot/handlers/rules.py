from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule
from vk_bot.handlers.states import user_states


class InRegistrationRule(ABCRule):
    """Кастомное правило: пользователь в процессе регистрации."""

    async def check(self, message: Message) -> bool:
        # Используем .get(), чтобы избежать KeyError, если ключа 'type' вдруг нет
        state = user_states.get(message.from_id)
        return state is not None and state.get('type') == 'registration'


class InAwardingRule(ABCRule):
    """Кастомное правило: пользователь в процессе начисления огоньков."""

    # ^^^ Исправил комментарий (было скопировано "регистрации")

    async def check(self, message: Message) -> bool:
        state = user_states.get(message.from_id)
        return state is not None and state.get('type') == 'award'

class InTextEditingRule(ABCRule):
    """Кастомное правило: пользователь в процессе редактирования текста."""

    async def check(self, message: Message) -> bool:
        state = user_states.get(message.from_id)
        return state is not None and state.get('type') == 'text_editing'

class InBroadcastingRule(ABCRule):
    """Кастомное правило: пользователь в процессе массовой рассылки."""

    async def check(self, message: Message) -> bool:
        state = user_states.get(message.from_id)
        return state is not None and state.get('type') == 'broadcast'


class NotInFSMRule(ABCRule):
    """Возвращает True, если пользователь не находится ни в одном активном процессе FSM."""

    async def check(self, message: Message) -> bool:
        state = user_states.get(message.from_id)

        # Если состояния нет вообще ИЛИ в состоянии нет ключа 'type' (оно пустое)
        if state is None or not state.get('type'):
            return True

        return False