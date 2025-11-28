from database import DatabaseManager


class ConsoleAnalyticsInterface:
    def __init__(self):
        self.db = DatabaseManager()

    def display_menu(self):
        print("\n=== СИСТЕМА УЧЕТА ЗАКАЗОВ - АНАЛИТИКА ===")
        print("1. Общая статистика")
        print("2. Популярные товары")
        print("3. Средний чек")
        print("4. Лучший клиент")
        print("5. Заказы по месяцам")
        print("6. Выручка по месяцам")
        print("0. Выход")

    def run(self):
        while True:
            self.display_menu()
            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.show_general_statistics()
            elif choice == '2':
                self.show_popular_products()
            elif choice == '3':
                self.show_average_order_value()
            elif choice == '4':
                self.show_best_customer()
            elif choice == '5':
                self.show_orders_by_month()
            elif choice == '6':
                self.show_revenue_by_month()
            elif choice == '0':
                print("Выход из программы...")
                break
            else:
                print("Неверный выбор!")

    def show_general_statistics(self):
        print("\n--- ОБЩАЯ СТАТИСТИКА ---")

        total_orders = self.db.get_orders_count()
        total_customers = self.db.get_customers_count()
        total_products = self.db.get_products_count()
        total_revenue = self.db.get_total_revenue()
        avg_order_value = self.db.get_average_order_value()

        print(f"📊 Общее количество заказов: {total_orders}")
        print(f"👥 Общее количество клиентов: {total_customers}")
        print(f"📦 Общее количество товаров: {total_products}")
        print(f"💰 Общая выручка: {total_revenue:.2f} руб.")
        print(f"💳 Средний чек: {avg_order_value:.2f} руб.")

        # Дополнительная статистика
        orders = self.db.get_all_orders()
        if orders:
            completed_orders = len([o for o in orders if o['status'] == 'completed'])
            pending_orders = len([o for o in orders if o['status'] == 'pending'])
            cancelled_orders = len([o for o in orders if o['status'] == 'cancelled'])

            print(f"\n📈 Статусы заказов:")
            print(f"   ✅ Выполнено: {completed_orders}")
            print(f"   ⏳ В ожидании: {pending_orders}")
            print(f"   ❌ Отменено: {cancelled_orders}")

            # Самый дорогой заказ
            if completed_orders > 0:
                max_order = max(orders, key=lambda x: x['total_amount'])
                print(f"\n🏆 Самый дорогой заказ:")
                print(f"   Заказ №{max_order['id']}: {max_order['total_amount']:.2f} руб.")
                print(f"   Клиент: {max_order['customer_name']}")

    def show_popular_products(self):
        print("\n--- ПОПУЛЯРНЫЕ ТОВАРЫ ---")

        try:
            limit = int(input("Сколько товаров показать? (по умолчанию 5): ") or "5")
        except ValueError:
            limit = 5

        popular_products = self.db.get_popular_products(limit)

        if not popular_products:
            print("Нет данных о продажах.")
            return

        print(f"\nТоп-{len(popular_products)} самых популярных товаров:")
        for i, (product_name, total_sold) in enumerate(popular_products, 1):
            print(f"{i}. {product_name}: {total_sold} шт.")

    def show_average_order_value(self):
        print("\n--- СРЕДНИЙ ЧЕК ---")

        avg_value = self.db.get_average_order_value()

        print(f"💳 Средний чек за все заказы: {avg_value:.2f} руб.")

        # Дополнительная аналитика по чекам
        orders = self.db.get_all_orders()
        if orders:
            completed_orders = [o for o in orders if o['status'] == 'completed']
            if completed_orders:
                order_values = [o['total_amount'] for o in completed_orders]
                min_value = min(order_values)
                max_value = max(order_values)

                print(f"📊 Анализ чеков выполненных заказов:")
                print(f"   Минимальный чек: {min_value:.2f} руб.")
                print(f"   Максимальный чек: {max_value:.2f} руб.")
                print(f"   Средний чек: {avg_value:.2f} руб.")

                # Распределение по диапазонам
                ranges = [0, 1000, 5000, 10000, 50000, float('inf')]
                range_labels = ["до 1,000", "1,000-5,000", "5,000-10,000", "10,000-50,000", "свыше 50,000"]

                print(f"\n📈 Распределение заказов по сумме:")
                for i in range(len(ranges) - 1):
                    count = len([v for v in order_values if ranges[i] <= v < ranges[i + 1]])
                    if count > 0:
                        percentage = (count / len(order_values)) * 100
                        print(f"   {range_labels[i]} руб.: {count} заказов ({percentage:.1f}%)")

    def show_best_customer(self):
        print("\n--- ЛУЧШИЙ КЛИЕНТ ---")

        best_customer_name, total_spent = self.db.get_best_customer()

        print(f"🏆 Лучший клиент: {best_customer_name}")
        print(f"💵 Общая сумма заказов: {total_spent:.2f} руб.")

        # Топ-5 клиентов
        print(f"\n📊 Топ-5 клиентов по сумме заказов:")

        conn = self.db._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.name, SUM(o.total_amount) as total_spent
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.status = 'completed'
            GROUP BY c.id, c.name
            ORDER BY total_spent DESC
            LIMIT 5
        ''')

        top_customers = cursor.fetchall()
        conn.close()

        for i, (name, spent) in enumerate(top_customers, 1):
            print(f"{i}. {name}: {spent:.2f} руб.")

    def show_orders_by_month(self):
        print("\n--- ЗАКАЗЫ ПО МЕСЯЦАМ ---")

        monthly_orders = self.db.get_orders_by_month()

        if not monthly_orders:
            print("Нет данных о заказах.")
            return

        print("📅 Количество заказов по месяцам:")
        total_orders = 0
        for month, order_count in monthly_orders:
            print(f"   {month}: {order_count} заказов")
            total_orders += order_count

        print(f"\n📈 Всего заказов за период: {total_orders}")

        if len(monthly_orders) > 1:
            # Анализ роста/падения
            first_month_count = monthly_orders[0][1]
            last_month_count = monthly_orders[-1][1]

            if first_month_count > 0:
                growth = ((last_month_count - first_month_count) / first_month_count) * 100
                trend = "рост" if growth > 0 else "падение"
                print(f"📊 {trend.capitalize()} за период: {abs(growth):.1f}%")

    def show_revenue_by_month(self):
        print("\n--- ВЫРУЧКА ПО МЕСЯЦАМ ---")

        monthly_revenue = self.db.get_revenue_by_month()

        if not monthly_revenue:
            print("Нет данных о выручке.")
            return

        print("💰 Выручка по месяцам:")
        total_revenue = 0
        for month, revenue in monthly_revenue:
            print(f"   {month}: {revenue:.2f} руб.")
            total_revenue += revenue

        print(f"\n📈 Общая выручка за период: {total_revenue:.2f} руб.")

        if len(monthly_revenue) > 1:
            # Анализ динамики
            first_month_revenue = monthly_revenue[0][1]
            last_month_revenue = monthly_revenue[-1][1]

            if first_month_revenue > 0:
                growth = ((last_month_revenue - first_month_revenue) / first_month_revenue) * 100
                trend = "рост" if growth > 0 else "падение"
                print(f"📊 {trend.capitalize()} выручки за период: {abs(growth):.1f}%")

            # Средняя месячная выручка
            avg_monthly = total_revenue / len(monthly_revenue)
            print(f"📊 Средняя месячная выручка: {avg_monthly:.2f} руб.")

    def _get_connection(self):
        """Вспомогательный метод для получения соединения (для аналитических запросов)"""
        import sqlite3
        return sqlite3.connect(self.db.db_name)