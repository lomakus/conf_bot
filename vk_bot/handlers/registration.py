import asyncio
from vkbottle.bot import Bot, Message
import logging
from database.queries import (
    get_user_by_vk_id,
    is_nickname_taken,
    add_user,
    get_user_by_id
)
from vk_bot.keyboards.main_menu import get_main_menu_keyboard, get_register_keyboard
from vk_bot.handlers.rules import InRegistrationRule
from vk_bot.utils.notifications import notify_new_registration

logger = logging.getLogger(__name__)

from vk_bot.handlers.states import user_states, clear_state

def register_handlers(bot: Bot):
    """Регистрирует хендлеры регистрации."""

    @bot.on.message(text=["/register", "зарегистрироваться"])
    @bot.on.message(payload_contains={"action": "register"})
    async def register_start(msg: Message):
        """Начало процесса регистрации."""
        # Проверка, не зарегистрирован ли уже
        if await get_user_by_vk_id(msg.from_id):
            await msg.answer("⛔ Ты уже зарегистрирован в системе.")
            return

        # Инициализируем состояние
        user_states[msg.from_id] = {
            "step": "full_name",
            "data": {},
            "type": 'registration'
        }
        await msg.answer("📝 Шаг 1/5\n\nВведи своё ФИО (полностью):")

    @bot.on.message(InRegistrationRule())
    async def registration_fsm(msg: Message):

        logger.info('Попалии в registration_fsm')
        """Единый хендлер для обработки всех шагов регистрации."""
        vk_id = msg.from_id

        # Если пользователь не в процессе регистрации, игнорируем
        if vk_id not in user_states:
            return

        state = user_states[vk_id]
        step = state["step"]
        text = msg.text.strip()

        # --- ШАГ 1: ФИО ---
        if step == "full_name":
            if len(text) < 3:
                await msg.answer("⚠️ ФИО слишком короткое. Попробуй ещё раз:")
                return

            state["data"]["full_name"] = text
            state["step"] = "nickname"
            await msg.answer("📝 Шаг 2/5\n\nПридумай никнейм (латиницей, без пробелов):")
            return

        # --- ШАГ 2: НИКНЕЙМ ---
        if step == "nickname":
            if not text.isalnum() or not text.isascii():
                await msg.answer("⚠️ Ник должен содержать только латинские буквы и цифры. Попробуй ещё раз:")
                return

            # Проверка на уникальность
            if await is_nickname_taken(text):
                await msg.answer("⚠️ Этот никнейм уже занят. Придумай другой:")
                return

            state["data"]["nickname"] = text
            state["step"] = "password"
            await msg.answer("📝 Шаг 3/5\n\nПридумай пароль (минимум 4 символа):")
            return

        # --- ШАГ 3: ПАРОЛЬ ---
        if step == "password":
            if len(text) < 4:
                await msg.answer("⚠️ Пароль слишком короткий (минимум 4 символа). Попробуй ещё раз:")
                return

            state["data"]["password"] = text
            state["step"] = "age"
            await msg.answer("📝 Шаг 4/5\n\nУкажи свой возраст (числом):")
            return

        # --- ШАГ 4: ВОЗРАСТ ---
        if step == "age":
            try:
                age = int(text)
                # if not (14 <= age <= 100):
                #     await msg.answer("⚠️ Возраст должен быть от 18 до 100 лет. Попробуй ещё раз:")
                #     return
            except ValueError:
                await msg.answer("⚠️ Это не число. Введи возраст цифрами:")
                return

            state["data"]["age"] = age
            state["step"] = "city"
            await msg.answer("📝 Шаг 5/5\n\nУкажи свой город:")
            return

        # --- ШАГ 5: ГОРОД и ФИНАЛ ---
        if step == "city":
            if len(text) < 2:
                await msg.answer("⚠️ Название города слишком короткое. Попробуй ещё раз:")
                return

            state["data"]["city"] = text

            # Сохраняем в БД
            user_id = await add_user(
                full_name=state["data"]["full_name"],
                nickname=state["data"]["nickname"],
                password=state["data"]["password"],
                age=state["data"]["age"],
                city=state["data"]["city"],
                role="participant",  # По умолчанию
                vk_id=vk_id  # Привязываем VK ID
            )

            if user_id:
                # Очищаем состояние
                clear_state(vk_id)

                logger.info(f"Успешная регистрация: {state['data']['nickname']} (VK ID: {vk_id})")

                full_user = await get_user_by_id(user_id)
                if full_user:
                    await notify_new_registration(bot, full_user)

                await msg.answer(
                    f"✅ Регистрация завершена!\n\n"
                    f"Добро пожаловать, {state['data']['full_name']}!\n"
                    f"Твой никнейм: @{state['data']['nickname']}\n"
                    f"Твой текущий баланс: 0 огоньков.",
                    keyboard=get_main_menu_keyboard()
                )
            else:
                await msg.answer("❌ Произошла ошибка при сохранении. Попробуй начать заново: /register")
                clear_state(vk_id)
            return

    @bot.on.message(text=["/cancel", "отмена", "назад"])
    async def cancel_registration(msg: Message):
        """Отмена регистрации."""
        if msg.from_id in user_states:
            clear_state(msg.from_id)
            await msg.answer("❌ Регистрация отменена. Чтобы начать заново, напиши /register")
        else:
            await msg.answer("Ты и так не в процессе регистрации.")

    # @bot.on.message()
    # async def catch_all_handler(msg: Message):
    #     """Ловит ВСЕ сообщения, которые не поймали другие хендлеры."""
    #     logger.info(f"DEBUG: Перехвачено сообщение. Текст: '{msg.text}', Payload: '{msg.payload}'")

# import asyncio
#
# from vkbottle.bot import Bot, Message
# from vkbottle.modules import logger
#
#
# def register_handlers(bot: Bot):
#     """Регистрирует хендлеры регистрации."""
#
#     @bot.on.message(text="/start1")
#     async def start_handler(msg: Message):
#         """Обработчик команды /start."""
#         await asyncio.sleep(1)
#         await msg.answer("Привет! Я бот конференции. Напиши /register для регистрации.")
#         logger.info(f"Пользователь {msg.from_id} запустил бота")
#
#     @bot.on.message(text="/start2")
#     async def start_handler(msg: Message):
#         """Обработчик команды /start."""
#         await asyncio.sleep(2)
#         await msg.answer("Привет! Я бот конференции. Напиши /register для регистрации.")
#         logger.info(f"Пользователь {msg.from_id} запустил бота")
#
#     @bot.on.message(text="/start3")
#     async def start_handler(msg: Message):
#         """Обработчик команды /start."""
#         await asyncio.sleep(3)
#         await msg.answer("Привет! Я бот конференции. Напиши /register для регистрации.")
#         logger.info(f"Пользователь {msg.from_id} запустил бота")
#
#
