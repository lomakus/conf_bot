import asyncio
from database.models import init_db
from database.queries import (
    add_user, delete_user, update_score, get_user_score,
    get_user_transactions, get_all_users, get_all_transactions, delete_all_users, delete_all_transactions
)


async def test_transactions():
    """Тесты для транзакций с created_by."""
    print("\n🧪 ТЕСТЫ ТРАНЗАКЦИЙ С AUDIT\n")

    await init_db()

    users = await get_all_users()
    print('Пользователи', *users)

    transs = await get_all_transactions()
    print('Транзакции:', *transs)

    print("\n🎉 ТЕСТЫ ПРОЙДЕНЫ!\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_transactions())
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()