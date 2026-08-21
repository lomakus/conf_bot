"""
Модуль запросов к базе данных конференции.
Все функции асинхронные (async/await).
"""
import aiosqlite
import logging
from .models import get_connection

logger = logging.getLogger(__name__)


# ============================================================
# СОЗДАНИЕ / УДАЛЕНИЕ
# ============================================================

async def add_user(
    full_name: str,
    nickname: str,
    password: str,
    age: int,
    city: str = None,
    role: str = "participant",
    telegram_id: int = None,
    vk_id: int = None,
) -> int | None:
    """
    Регистрирует нового пользователя.
    Возвращает ID нового пользователя или None при ошибке (дубликат ника и т.д.).
    """
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO users 
                (full_name, nickname, password, age, city, role, telegram_id, vk_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, nickname, password, age, city, role, telegram_id, vk_id),
        )
        await conn.commit()
        user_id = cursor.lastrowid
        logger.info("Зарегистрирован пользователь: %s (ID: %d, роль: %s)", nickname, user_id, role)
        return user_id
    except aiosqlite.IntegrityError as e:
        logger.warning("Не удалось добавить пользователя %s: %s", nickname, e)
        return None
    finally:
        await conn.close()


async def delete_user(user_id: int) -> bool:
    """Удаляет пользователя по ID. Возвращает True, если строка удалена."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("Удалён пользователь ID: %d", user_id)
        return deleted
    finally:
        await conn.close()


# ============================================================
# ЧТЕНИЕ (поиск одного пользователя)
# ============================================================

async def get_user_by_id(user_id: int) -> dict | None:
    """Получить пользователя по внутреннему ID."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def get_user_by_nickname(nickname: str) -> dict | None:
    """Получить пользователя по нику (для авторизации)."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT * FROM users WHERE nickname = ?", (nickname,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def get_user_by_telegram_id(telegram_id: int) -> dict | None:
    """Получить пользователя по Telegram ID."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def get_user_by_vk_id(vk_id: int) -> dict | None:
    """Получить пользователя по VK ID."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT * FROM users WHERE vk_id = ?", (vk_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


# ============================================================
# АВТОРИЗАЦИЯ
# ============================================================

async def authenticate_user(nickname: str, password: str) -> dict | None:
    """
    Проверяет логин и пароль.
    Возвращает словарь пользователя при успехе, None при неудаче.
    """
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT * FROM users WHERE nickname = ? AND password = ?",
            (nickname, password),
        )
        row = await cursor.fetchone()
        if row:
            logger.info("Авторизация успешна: %s", nickname)
        else:
            logger.warning("Неудачная попытка авторизации: %s", nickname)
        return dict(row) if row else None
    finally:
        await conn.close()


async def is_nickname_taken(nickname: str) -> bool:
    """Проверяет, занят ли ник. Используется при регистрации."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT 1 FROM users WHERE nickname = ? LIMIT 1", (nickname,)
        )
        row = await cursor.fetchone()
        return row is not None
    finally:
        await conn.close()


# ============================================================
# ОБНОВЛЕНИЕ (привязка аккаунтов, смена данных)
# ============================================================

async def update_telegram_id(user_id: int, telegram_id: int) -> bool:
    """Привязывает Telegram ID к пользователю."""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE users SET telegram_id = ? WHERE id = ?", (telegram_id, user_id)
        )
        await conn.commit()
        logger.info("Привязан telegram_id=%d к пользователю ID=%d", telegram_id, user_id)
        return True
    except aiosqlite.IntegrityError as e:
        logger.warning("Не удалось привязать telegram_id: %s", e)
        return False
    finally:
        await conn.close()


async def update_vk_id(user_id: int, vk_id: int) -> bool:
    """Привязывает VK ID к пользователю."""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE users SET vk_id = ? WHERE id = ?", (vk_id, user_id)
        )
        await conn.commit()
        logger.info("Привязан vk_id=%d к пользователю ID=%d", vk_id, user_id)
        return True
    except aiosqlite.IntegrityError as e:
        logger.warning("Не удалось привязать vk_id: %s", e)
        return False
    finally:
        await conn.close()


async def update_password(user_id: int, new_password: str) -> bool:
    """Меняет пароль пользователя."""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE users SET password = ? WHERE id = ?", (new_password, user_id)
        )
        await conn.commit()
        logger.info("Сменён пароль для пользователя ID=%d", user_id)
        return True
    finally:
        await conn.close()


async def update_role(user_id: int, new_role: str) -> bool:
    """Меняет роль пользователя (admin, staff, participant)."""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE users SET role = ? WHERE id = ?", (new_role, user_id)
        )
        await conn.commit()
        logger.info("Изменена роль пользователя ID=%d на '%s'", user_id, new_role)
        return True
    except aiosqlite.IntegrityError as e:
        logger.warning("Не удалось изменить роль: %s", e)
        return False
    finally:
        await conn.close()


async def update_profile(
    user_id: int,
    full_name: str = None,
    age: int = None,
    city: str = None,
) -> bool:
    """Обновляет профиль пользователя (ФИО, возраст, город)."""
    fields = []
    values = []

    if full_name is not None:
        fields.append("full_name = ?")
        values.append(full_name)
    if age is not None:
        fields.append("age = ?")
        values.append(age)
    if city is not None:
        fields.append("city = ?")
        values.append(city)

    if not fields:
        return False

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"

    conn = await get_connection()
    try:
        await conn.execute(query, values)
        await conn.commit()
        logger.info("Обновлён профиль пользователя ID=%d", user_id)
        return True
    except aiosqlite.IntegrityError as e:
        logger.warning("Не удалось обновить профиль: %s", e)
        return False
    finally:
        await conn.close()


# ============================================================
# СПИСКИ И СТАТИСТИКА (для админа)
# ============================================================

async def get_all_users() -> list[dict]:
    """Получить всех пользователей (для админки)."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_users_by_role(role: str) -> list[dict]:
    """Получить пользователей по роли."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT * FROM users WHERE role = ? ORDER BY full_name", (role,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def search_users(query: str) -> list[dict]:
    """
    Поиск пользователей по ФИО, нику или городу.
    Используется LIKE для частичного совпадения.
    """
    conn = await get_connection()
    try:
        search_pattern = f"%{query}%"
        cursor = await conn.execute(
            """
            SELECT * FROM users 
            WHERE full_name LIKE ? OR nickname LIKE ? OR city LIKE ?
            ORDER BY full_name
            """,
            (search_pattern, search_pattern, search_pattern),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def get_stats() -> dict:
    """
    Статистика для админа.
    Возвращает словарь с количеством пользователей по ролям и городам.
    """
    conn = await get_connection()
    try:
        # Общее количество
        cursor = await conn.execute("SELECT COUNT(*) as total FROM users")
        total = (await cursor.fetchone())["total"]

        # По ролям
        cursor = await conn.execute(
            "SELECT role, COUNT(*) as count FROM users GROUP BY role"
        )
        by_role = {row["role"]: row["count"] for row in await cursor.fetchall()}

        # По городам (топ-10)
        cursor = await conn.execute(
            """
            SELECT city, COUNT(*) as count FROM users 
            WHERE city IS NOT NULL 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 10
            """
        )
        by_city = {row["city"]: row["count"] for row in await cursor.fetchall()}

        return {
            "total": total,
            "by_role": by_role,
            "by_city": by_city,
        }
    finally:
        await conn.close()


# ============================================================
# ТРАНЗАКЦИИ И SCORE
# ============================================================

async def add_transaction(
        user_id: int,
        amount: int,
        type: str,
        description: str = None,
        created_by: int = None,
) -> int | None:
    """
    Создаёт запись о транзакции.
    type: 'credit' (начисление) или 'debit' (списание).
    created_by: ID пользователя, который выполнил операцию (админ/служитель).
    Возвращает ID транзакции или None при ошибке.
    """
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            INSERT INTO transactions (user_id, amount, type, description, created_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, type, description, created_by),
        )
        await conn.commit()
        transaction_id = cursor.lastrowid
        logger.info(
            "Транзакция #%d: user_id=%d, %s %d, created_by=%s (%s)",
            transaction_id, user_id, type, amount, created_by or "система", description or "без описания"
        )
        return transaction_id
    except aiosqlite.IntegrityError as e:
        logger.warning("Не удалось создать транзакцию: %s", e)
        return None
    finally:
        await conn.close()


async def update_score(
        user_id: int,
        delta: int,
        description: str = None,
        created_by: int = None,
) -> int:
    """
    Изменяет score пользователя на delta (может быть положительным или отрицательным).
    Автоматически создаёт транзакцию.
    created_by: ID пользователя, который выполнил операцию.
    """
    conn = await get_connection()
    try:
        # Получаем текущий score
        cursor = await conn.execute("SELECT score FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return False

        current_score = row["score"]
        new_score = current_score + delta

        # Не даём уйти в минус
        if new_score < 0:
            logger.warning("Попытка уйти в минус: user_id=%d, score=%d, delta=%d", user_id, current_score, delta)
            return False

        # Обновляем score
        await conn.execute("UPDATE users SET score = ? WHERE id = ?", (new_score, user_id))

        # Создаём транзакцию
        tx_type = "credit" if delta > 0 else "debit"
        # trans_id = await add_transaction(user_id, abs(delta), tx_type, description or f"Изменение score: {delta:+d}", created_by)
        cursor = await conn.execute(
            """
            INSERT INTO transactions (user_id, amount, type, description, created_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, abs(delta), tx_type, description or f"Изменение score: {delta:+d}", created_by),
        )

        await conn.commit()

        transaction_id = cursor.lastrowid
        logger.info(
            "Score обновлён: user_id=%d, %d -> %d, created_by=%s",
            user_id, current_score, new_score, created_by or "система"
        )
        return transaction_id
    except aiosqlite.IntegrityError as e:
        logger.warning("Ошибка обновления score: %s", e)
        return False
    finally:
        await conn.close()


async def get_user_score(user_id: int) -> int | None:
    """Возвращает текущий score пользователя или None, если пользователь не найден."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT score FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return row["score"] if row else None
    finally:
        await conn.close()


async def get_user_transactions(user_id: int, limit: int = 50) -> list[dict]:
    """
    Возвращает историю транзакций пользователя (новые сверху).
    Включает информацию о том, кто начислил/снял очки.
    """
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT 
                t.id,
                t.amount,
                t.type,
                t.description,
                t.created_at,
                u.full_name as created_by_name,
                u.nickname as created_by_nickname
            FROM transactions t
            LEFT JOIN users u ON t.created_by = u.id
            WHERE t.user_id = ?
            ORDER BY t.created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_all_transactions() -> list[dict]:
    """Получить всех пользователей (для админки)."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT * FROM transactions ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_top_users(limit: int = 10) -> list[dict]:
    """Возвращает топ пользователей по score (для рейтинга)."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT id, full_name, nickname, score, city, role
            FROM users
            WHERE score > 0
            ORDER BY score DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_users_by_role(role: str) -> list[dict]:
    """Получает всех пользователей с определённой ролью, у которых есть vk_id."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT id, vk_id, full_name, nickname, role 
            FROM users 
            WHERE role = ? AND vk_id IS NOT NULL
            """,
            (role,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# ============================================================
# МАССОВОЕ УДАЛЕНИЕ (для тестирования и админки)
# ============================================================

async def delete_all_transactions() -> int:
    """
    Удаляет ВСЕ транзакции из базы данных.
    Возвращает количество удалённых записей.
    """
    conn = await get_connection()
    try:
        cursor = await conn.execute("DELETE FROM transactions")
        await conn.commit()
        deleted_count = cursor.rowcount
        logger.warning("Удалены ВСЕ транзакции: %d записей", deleted_count)
        return deleted_count
    finally:
        await conn.close()


async def delete_all_users() -> int:
    """
    Удаляет ВСЕХ пользователей из базы данных.
    Из-за ON DELETE CASCADE автоматически удаляются все транзакции.
    Возвращает количество удалённых пользователей.
    """
    conn = await get_connection()
    try:
        cursor = await conn.execute("DELETE FROM users")
        await conn.commit()
        deleted_count = cursor.rowcount
        logger.warning("Удалены ВСЕ пользователи: %d записей (и все их транзакции)", deleted_count)
        return deleted_count
    finally:
        await conn.close()


async def reset_database() -> dict:
    """
    Полный сброс базы данных: удаляет всех пользователей и все транзакции.
    Возвращает статистику удалённых записей.
    """
    conn = await get_connection()
    try:
        # Считаем количество записей перед удалением
        cursor = await conn.execute("SELECT COUNT(*) as count FROM transactions")
        tx_count = (await cursor.fetchone())["count"]

        cursor = await conn.execute("SELECT COUNT(*) as count FROM users")
        user_count = (await cursor.fetchone())["count"]

        # Удаляем всё (порядок важен из-за FOREIGN KEY)
        await conn.execute("DELETE FROM transactions")
        await conn.execute("DELETE FROM users")
        await conn.commit()

        logger.warning(
            "Полный сброс БД: удалено %d пользователей и %d транзакций",
            user_count, tx_count
        )

        return {
            "users_deleted": user_count,
            "transactions_deleted": tx_count,
        }
    finally:
        await conn.close()

# ============================================================
# СТАТИСТИКА
# ============================================================

async def get_users_stats() -> dict:
    """Возвращает статистику по ролям пользователей."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("""
            SELECT 
                role,
                COUNT(*) as count
            FROM users
            GROUP BY role
        """)
        rows = await cursor.fetchall()

        stats = {
            'total': 0,
            'participant': 0,
            'staff': 0,
            'admin': 0
        }

        for row in rows:
            role = row['role']
            count = row['count']
            stats[role] = count
            stats['total'] += count

        return stats
    finally:
        await conn.close()

# ============================================================
# ТЕКСТОВЫЕ ВСТАВКИ
# ============================================================

async def get_text(key: str) -> str | None:
    """Получает текст по ключу."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT text FROM texts WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        return row['text'] if row else None
    finally:
        await conn.close()


async def set_text(key: str, text: str, description: str = '') -> bool:
    """Обновляет или создает текст по ключу."""
    conn = await get_connection()
    try:
        await conn.execute(
            """
            INSERT INTO texts (key, text, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                text = excluded.text,
                description = excluded.description,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, text, description)
        )
        await conn.commit()
        logger.info(f"Текст '{key}' обновлен")
        return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении текста '{key}': {e}")
        return False
    finally:
        await conn.close()


async def get_all_texts() -> list[dict]:
    """Получает все тексты (для админки)."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT key, text, description, updated_at FROM texts ORDER BY key"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()


# ============================================================
# СТАТИСТИКА И АНАЛИТИКА
# ============================================================

async def get_recent_transactions(limit: int = 30) -> list[dict]:
    """Возвращает последние транзакции с данными пользователей."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT 
                t.id,
                t.amount,
                t.type,
                t.description,
                t.created_at,
                u.full_name as user_name,
                u.nickname as user_nickname,
                c.full_name as creator_name,
                c.nickname as creator_nickname
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN users c ON t.created_by = c.id
            ORDER BY t.created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await conn.close()