import os
import aiosqlite
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "conference.db")

async def get_connection():
    """Возвращает асинхронное подключение к БД."""
    conn = await aiosqlite.connect(DB_NAME, timeout=10)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    return conn

async def init_db():
    """Создает таблицу users, если её нет."""
    conn = await get_connection()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                nickname TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                city TEXT,
                score INTEGER DEFAULT 0,
                role TEXT NOT NULL DEFAULT 'participant' CHECK(role IN ('admin', 'staff', 'participant')),
                telegram_id INTEGER UNIQUE,
                vk_id INTEGER UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица транзакций (с полем created_by)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('credit', 'debit')),
                description TEXT,
                created_by INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                text TEXT NOT NULL,
                description TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await init_default_texts(conn)

        await conn.commit()
        logger.info("✅ База данных конференции инициализирована.")
    finally:
        await conn.close()

async def init_default_texts(conn):
    """Заполняет таблицу texts дефолтными значениями."""
    default_texts = [
        {
            'key': 'faq_earn',
            'text': (
                "💰 КАК ЗАРАБОТАТЬ ОГОНЬКИ?\n\n"
                "Есть два типа заданий: через бота (отправляешь фото) и через служителя (проверка лично).\n\n"

                "📸 ЗАДАНИЯ ЧЕРЕЗ БОТА\n"
                "Нажми кнопку «📸 Отправить фото» и отправь снимок. Служители проверят и начислят огоньки.\n\n"
                "Примеры заданий:\n"
                "• Сфоткаться с 5 незнакомыми людьми\n"
                "• Сфоткаться с человеком из другого города\n"
                "• Сфоткаться с человеком в необычном образе/аксессуаре\n"
                "• Сфоткаться всей компанией из 5–10 человек\n"
                "• Сфоткаться с несколькими служителями\n"
                "• Сделать фото с человеком, которого впервые сегодня встретил\n"
                "• Найти человека в красной футболке и сделать совместное фото\n"
                "• Сделать самое необычное фото\n"
                "• Воссоздать мем/картинку командой и отправить фото\n\n"

                "🛡 ЗАДАНИЯ ЧЕРЕЗ СЛУЖИТЕЛЯ\n"
                "Подойди к служителю — он проверит и начислит огоньки.\n\n"
                "Примеры заданий:\n"
                "• Рассказать стих из Библии\n"
                "• Найти указанный стих в бумажной Библии\n"
                "• Ответить на вопрос по проповеди\n"
                "• Назвать 3 факта/мысли из проповеди\n"
                "• Познакомиться с 5 незнакомцами и назвать их имена\n"
                "• Привести человека, с которым только что познакомился, и вместе выполнить мини-задание\n"
                "• Смонтировать влог дня о конфе (лучшие покажем на вечернем служении)\n"
                "• Сделать конспект проповеди конференции\n"
                "• Победа в турнирах (огоньки можно получить и за участие)\n"
                "• Раскраски в чилл-зоне\n"
                "• Побить рекорды в зоне рекордов"
            ),
            'description': 'FAQ: Как заработать огоньки'
        },
        {
            'key': 'faq_spend',
            'text': (
                "🎁 НА ЧТО ТРАТИТЬ ОГОНЬКИ?\n\n"
                "Огоньки — это твоя валюта на конференции! Меняй их на вкусняшки, развлечения и крутые призы.\n\n"

                "🍿 ЕДА И НАПИТКИ\n"
                "• Попкорн — классика для уютного вечера\n"
                "• Сладкая вата — сладкое наслаждение\n"
                "• Магазин с колой и шококроко — освежись и подсласти день\n\n"

                "🎮 РАЗВЛЕЧЕНИЯ\n"
                "• Плейстейшн — поиграй в любимые игры\n"
                "• Нинтендо — весёлые игры для компании\n\n"

                "🎯 ПРИЗЫ И УДАЧА\n"
                "• Лототрон с призами — испытай удачу и выиграй крутой приз\n"
                "• Дартс с призами — меткий бросок = классный подарок\n\n"

                "💡 КАК ПОЛУЧИТЬ ТОВАР?\n"
                "Подойди к служителю в зоне обмена, покажи свой баланс и выбери, на что хочешь потратить огоньки. Служитель спишет нужное количество и выдаст тебе товар или доступ к развлечению.\n\n"

                "🔥 СОВЕТ\n"
                "Не копи огоньки до последнего дня — трать с умом и наслаждайся конференцией на полную!\n"
                "Лучшие призы разбирают быстро 😉"
            ),
            'description': 'FAQ: На что тратить огоньки'
        },
        {
            'key': 'welcome_message',
            'text': (
                "👋 Привет! Я бот конференции Огонь!\n\n"
                "Помогу тебе заработать огоньки, отслеживать баланс и участвовать в активностях.\n\n"

                "⚠️ ВАЖНО\n"
                "Нажимая кнопку «📝 Зарегистрироваться», ты даёшь согласие на обработку персональных данных в соответствии с правилами конференции.\n\n"

                "Готов начать? Нажми кнопку ниже 👇\n"
                "(Можешь нажать войти, если ты уже регистрировался в другом боте)"
            ),
            'description': 'Приветственное сообщение с согласием на обработку ПДн'
        },
        {
            'key': 'shop',
            'text': (
                "🛒 МАГАЗИН\n\n"
                "Ты можешь обменять огоньки на следующие товары:\n\n"

                "🍿 ЕДА И НАПИТКИ\n"
                "• Попкорн\n"
                "• Сладкая вата\n"
                "• Кола\n"
                "• Шококроко\n\n"

                "🎮 РАЗВЛЕЧЕНИЯ\n"
                "• Плейстейшн\n"
                "• Нинтендо\n\n"

                "🎯 ПРИЗЫ И УДАЧА\n"
                "• Лототрон\n"
                "• Дартс\n\n"

                "💡 КАК ПОЛУЧИТЬ ТОВАР?\n"
                "Подойди к служителю, покажи свой баланс и выбери товар. Служитель спишет огоньки и выдаст тебе товар.\n\n"

                "🔥 СОВЕТ\n"
                "Не копи огоньки до последнего дня — трать с умом и наслаждайся конференцией!"
            ),
            'description': 'Магазин - список товаров'
        }
    ]

    for item in default_texts:
        try:
            await conn.execute(
                """
                INSERT OR IGNORE INTO texts (key, text, description)
                VALUES (?, ?, ?)
                """,
                (item['key'], item['text'], item['description'])
            )
        except Exception as e:
            logger.warning(f"Не удалось добавить текст {item['key']}: {e}")

    await conn.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
    print(f"✅ Таблица users создана в файле: {DB_NAME}")