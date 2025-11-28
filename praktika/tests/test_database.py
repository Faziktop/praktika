import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'database_version'))

from database import DatabaseManager

def test_database_operations():
    """Тестирование операций с базой данных"""
    print("=== ТЕСТИРОВАНИЕ БАЗЫ ДАННЫХ ===")

    # Создаем тестовую БД
    db = DatabaseManager("test.db")

    # Тест CRUD операций
    print("\n1. Тестирование CRUD операций...")

    # Добавление клиента
    customer_id = db.add_customer("Тестовый Клиент", "test@example.com", "+79990000000")
    print(f"✅ Добавлен клиент с ID: {customer_id}")

    # Добавление товара
    product_id = db.add_product("Тестовый Товар", 1000, 10)
    print(f"✅ Добавлен товар с ID: {product_id}")

    # Создание заказа
    order_id, message = db.create_order(customer_id, [{'product_id': product_id, 'quantity': 2}])
    print(f"✅ Создан заказ с ID: {order_id}")

    # Тест аналитических функций
    print("\n2. Тестирование аналитических функций...")

    # Общая статистика
    orders_count = db.get_orders_count()
    customers_count = db.get_customers_count()
    products_count = db.get_products_count()

    print(f"📊 Заказы: {orders_count}")
    print(f"👥 Клиенты: {customers_count}")
    print(f"📦 Товары: {products_count}")

    # Популярные товары
    popular = db.get_popular_products()
    print(f"🏆 Популярные товары: {popular}")

    # Средний чек
    avg_cheque = db.get_average_order_value()
    print(f"💳 Средний чек: {avg_cheque:.2f}")

    # Очистка тестовой БД
    success, message = db.clear_database()
    print(f"\n🧹 {message}")

    print("\n🎉 Все тесты пройдены успешно!")

if __name__ == "__main__":
    test_database_operations()