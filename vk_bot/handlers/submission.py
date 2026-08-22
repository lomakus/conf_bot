from vkbottle.bot import Bot, Message
from vkbottle.modules import logger
from database.queries import get_user_by_vk_id
from vk_bot.keyboards.main_menu import get_main_menu_keyboard
from config import VK_REVIEW_CHAT_ID


def register_phot_handlers(bot: Bot):
    """Регистрирует хендлер простой отправки фото в чат проверки."""
    @bot.on.message(payload_contains={"action": "submit_photo"})
    async def submit_photo_prompt(msg: Message):
        """Просит пользователя отправить фото."""
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer("⛔ Ты не зарегистрирован. Напиши /start")
            return

        await msg.answer(
            "📸 Отправка фото на проверку\n\n"
            "Отправь фото одним сообщением.\n"
            "Оно будет отправлено служителям на проверку.",
            keyboard=get_main_menu_keyboard(user['role'])
        )

    @bot.on.message(attachment="photo")
    async def handle_photo(msg: Message):
        # 1. Проверяем, зарегистрирован ли пользователь
        user = await get_user_by_vk_id(msg.from_id)
        if not user:
            await msg.answer(
                "⛔ Ты не зарегистрирован. Напиши /start",
                keyboard=get_main_menu_keyboard(user['role'])
            )
            return

        # 2. Берем данные пользователя
        full_name = user['full_name']
        nickname = user['nickname']

        # 3. Отправляем в чат проверки
        if VK_REVIEW_CHAT_ID:
            try:
                # Пересылаем сообщение с фото целиком
                await bot.api.messages.send(
                    peer_id=int(VK_REVIEW_CHAT_ID),
                    forward_messages=str(msg.id),
                    message=f"📸 Новое фото на проверку\n👤 От: {full_name} ({nickname})",
                    random_id=0,
                )
                logger.info(f"✅ Фото от {nickname} успешно отправлено в чат проверки")
            except Exception as e:
                logger.error(f"❌ Ошибка отправки фото в чат: {e}")
                await msg.answer(
                    "❌ Произошла ошибка при отправке фото. Попробуй позже.",
                    keyboard=get_main_menu_keyboard(user['role'])
                )
                return
        else:
            logger.error("⚠️ VK_REVIEW_CHAT_ID не настроен в .env!")
            await msg.answer(
                "❌ Чат проверки не настроен. Сообщите администратору.",
                keyboard=get_main_menu_keyboard(user['role'])
            )
            return

        # 4. Отвечаем пользователю, что всё ок
        await msg.answer(
            "✅ Фото успешно отправлено на проверку!",
            keyboard=get_main_menu_keyboard(user['role'])
        )