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

    # 1. Создаём админа (кто будет начислять)
    print("1. Создание админа...")
    admin_id = await add_user("Админ Админов", "admin", "pass", 30, "Москва", "admin")
    assert admin_id is not None
    print(f"   ✅ Админ ID: {admin_id}")

    # 2. Создаём участника
    print("2. Создание участника...")
    user_id = await add_user("Участник Участников", "user", "pass", 25, "СПб", "participant")
    assert user_id is not None
    print(f"   ✅ Участник ID: {user_id}")

    # 3. Начисляем очки от имени админа
    print("3. Начисление +100 от админа...")
    ok = await update_score(user_id, 100, description="За активность", created_by=admin_id)
    assert ok
    score = await get_user_score(user_id)
    assert score == 100
    print(f"   ✅ Score: {score}")

    # 4. Снимаем очки от имени админа
    print("4. Списание -30 от админа...")
    ok = await update_score(user_id, -30, description="Штраф", created_by=admin_id)
    assert ok
    score = await get_user_score(user_id)
    assert score == 70
    print(f"   ✅ Score: {score}")

    # 5. Проверяем историю транзакций
    print("5. История транзакций...")
    txs = await get_user_transactions(user_id)
    assert len(txs) == 2
    print(f"   ✅ Найдено транзакций: {len(txs)}")
    for tx in txs:
        created_by_info = f"от {tx['created_by_name']} (@{tx['created_by_nickname']})" if tx['created_by_name'] else "от системы"
        print(f"      - {tx['type']}: {tx['amount']} ({tx['description']}) {created_by_info}")

    # 6. Удаляем админа — транзакции должны остаться, но created_by станет NULL
    print("6. Удаление админа...")
    await delete_user(admin_id)
    txs = await get_user_transactions(user_id)
    assert len(txs) == 2, "Транзакции должны остаться!"
    for tx in txs:
        assert tx['created_by_name'] is None, "created_by должен стать NULL!"
    print("   ✅ Админ удалён, транзакции остались, created_by = NULL")

    # 7. Очистка
    print("7. Очистка...")
    await delete_user(user_id)

    print("   ✅ Удалено")

    users = await get_all_users()
    print('Пользователи', users)

    transs = await get_all_transactions()
    print('Транзакции:', transs)

    deleted_users = await delete_all_users()
    deleted_transs = await delete_all_transactions()

    print(deleted_users)
    print(deleted_transs)

    users = await get_all_users()
    print('Пользователи', users)

    transs = await get_all_transactions()
    print('Транзакции:', transs)

    print("\n🎉 ТЕСТЫ ПРОЙДЕНЫ!\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_transactions())
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()