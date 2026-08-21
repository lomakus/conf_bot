import json
from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import (
    get_user_by_vk_id,
    get_user_by_nickname,
    get_user_transactions,
    update_score
)
from vk_bot.keyboards.main_menu import get_main_menu_keyboard
from vk_bot.handlers.states import user_states, clear_state
from vk_bot.handlers.rules import InAwardingRule
from vk_bot.utils.notifications import notify_score_change


def register_award_handlers(bot: Bot):
    """Регистрирует хендлеры для начисления жетонов служителями."""

    @bot.on.message(payload_contains={"action": "award_tokens"})
    async def start_award(msg: Message):
        """Начало процесса начисления."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user or user['role'] not in ('staff', 'admin'):
            await msg.answer("⛔ Эта функция доступна только служителям и админам.")
            return

        # Инициализируем состояние
        user_states[msg.from_id] = {
            "step": "awaiting_nickname",
            "data": {},
            "type": 'award'
        }
        await msg.answer("💰 Начисление жетонов\n\nВведите никнейм участника:")

    @bot.on.message(InAwardingRule())
    async def award_fsm(msg: Message):
        """FSM для обработки шагов начисления."""
        vk_id = msg.from_id

        state = user_states[vk_id]
        step = state["step"]
        text = msg.text.strip() if msg.text else ""

        staff_user = await get_user_by_vk_id(vk_id)  # Тот, кто начисляет

        # --- ШАГ 1: Ввод никнейма ---
        if step == "awaiting_nickname":
            target = await get_user_by_nickname(text)
            if not target:
                await msg.answer("⚠️ Участник с таким никнеймом не найден. Попробуйте ещё раз или напишите /cancel")
                return

            state["data"]["target_user"] = target
            state["step"] = "awaiting_amount"

            # Получаем последние 3 транзакции
            txs = await get_user_transactions(target['id'], limit=3)
            tx_history = "\n".join([
                f"  • {'+' if t['type'] == 'credit' else '-'}{t['amount']} жет. ({t['description'] or 'без причины'})"
                for t in txs
            ]) or "  • История пуста"

            await msg.answer(
                f"✅ Участник найден:\n"
                f"👤 ФИО: {target['full_name']}\n"
                f"💰 Текущий баланс: {target['score']} жетонов\n\n"
                f"📜 Последние 3 операции:\n{tx_history}\n\n"
                f"Введите количество жетонов для начисления/списания (число):"
            )
            return

        # --- ШАГ 2: Ввод количества ---
        if step == "awaiting_amount":
            try:
                amount = int(text)
                # if amount <= 0:
                #     await msg.answer("⚠️ Количество должно быть больше 0. Введите число:")
                #     return

                state["data"]["amount"] = amount
                state["step"] = "awaiting_reason"
                await msg.answer("Введите причину начисления/списания (текст):")
            except ValueError:
                await msg.answer("⚠️ Это не число. Введите количество жетонов цифрами:")
            return

        # --- ШАГ 3: Ввод причины и финал ---
        if step == "awaiting_reason":
            reason = text
            target = state["data"]["target_user"]
            amount = state["data"]["amount"]

            # Обновляем баланс и создаем транзакцию
            success = await update_score(
                user_id=target['id'],
                delta=amount,
                description=reason,
                created_by=staff_user['id']
            )

            if success:
                clear_state(vk_id)
                new_balance = target['score'] + amount

                # Отправляем уведомление
                await notify_score_change(
                    bot=bot,
                    transaction_id=success,
                    participant=target,
                    amount=amount,
                    tx_type='credit' if amount >= 0 else 'debit',
                    reason=reason,
                    staff=staff_user
                )

                await msg.answer(
                    f"✅ Успешно!\n\n"
                    f"{target['role']} {target['nickname']} ({target['full_name']}) начислено {amount} жетонов от {staff_user['role']} {staff_user['nickname']} ({staff_user['full_name']}).\n"
                    f"Причина: {reason}\n"
                    f"Новый баланс участника: {new_balance}",
                    keyboard=get_main_menu_keyboard(staff_user['role'])
                )
                logger.info(
                    f"Служитель {staff_user['nickname']} начислил {amount} жетонов участнику {target['nickname']}")

                # Уведомляем участника в личку (если у него есть vk_id)
                if target['vk_id']:
                    try:
                        await bot.api.messages.send(
                            user_id=target['vk_id'],
                            message=(
                                f"🎉 Вам начислено {amount} жетонов!\n\n"
                                f"Причина: {reason}\n"
                                f"Начислил: {staff_user['full_name']}"
                            ),
                            random_id=0,
                        )
                    except Exception as e:
                        logger.warning(f"Не удалось уведомить участника {target['vk_id']}: {e}")
            else:
                await msg.answer("❌ Ошибка при сохранении в базу данных. Попробуйте позже.")
                clear_state(vk_id)
            return

    @bot.on.message(text=["/cancel", "отмена"])
    async def cancel_award(msg: Message):
        """Отмена процесса начисления."""
        if msg.from_id in user_states and user_states[msg.from_id]["step"].startswith("awaiting_"):
            clear_state(msg.from_id)
            user = await get_user_by_vk_id(msg.from_id)
            role = user['role'] if user else 'participant'
            await msg.answer(
                "❌ Операция отменена.",
                keyboard=get_main_menu_keyboard(role)
            )
        else:
            # Если не в процессе начисления, пусть ловит другой хендлер или игнорирует
            pass