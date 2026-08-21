import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import init_db
from database.queries import (
    add_user, get_user_by_nickname, get_user_by_telegram_id,
    authenticate_user, is_nickname_taken, update_vk_id,
    get_all_users, get_users_by_role, search_users, get_stats,
    delete_user, update_role, update_profile
)


async def run_tests():
    print("\n🧪 ТЕСТЫ БАЗЫ ДАННЫХ КОНФЕРЕНЦИИ\n")

    await init_db()

    # 1. Регистрация
    print("1. Регистрация...")
    uid = await add_user("Иван Иванов", "ivan", "pass123", 25, "Москва", "participant", telegram_id=111)
    users = await get_all_users()

    print(users)


    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!\n")


if __name__ == "__main__":
    # try:
    #     asyncio.run(run_tests())
    # except Exception as e:
    #     print(f"\n❌ ОШИБКА: {e}")
    #     import traceback
    #     traceback.print_exc()

    print('1')
    asyncio.run(run_tests())

