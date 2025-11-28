import sqlite3
from datetime import datetime
from models import Customer, Product, Order


class DatabaseManager:
    def __init__(self, db_name="orders.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        conn.commit()
        conn.close()

    # CRUD для клиентов
    def add_customer(self, name, email, phone):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                (name, email, phone)
            )
            conn.commit()
            customer_id = cursor.lastrowid
            return customer_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_all_customers(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = []
        for row in cursor.fetchall():
            customers.append(Customer(id=row[0], name=row[1], email=row[2], phone=row[3]))
        conn.close()
        return customers

    def get_customer_by_id(self, customer_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Customer(id=row[0], name=row[1], email=row[2], phone=row[3])
        return None

    def update_customer(self, customer_id, name=None, email=None, phone=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if phone:
            updates.append("phone = ?")
            params.append(phone)

        if not updates:
            return False

        params.append(customer_id)
        query = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_customer(self, customer_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,))
        order_count = cursor.fetchone()[0]

        if order_count > 0:
            conn.close()
            return False, "Нельзя удалить клиента с существующими заказами"

        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success, "Клиент удален" if success else "Клиент не найден"

    # CRUD для товаров
    def add_product(self, name, price, quantity):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            (name, price, quantity)
        )
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id

    def get_all_products(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = []
        for row in cursor.fetchall():
            products.append(Product(id=row[0], name=row[1], price=row[2], quantity=row[3]))
        conn.close()
        return products

    def get_product_by_id(self, product_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Product(id=row[0], name=row[1], price=row[2], quantity=row[3])
        return None

    def update_product(self, product_id, name=None, price=None, quantity=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)

        if not updates:
            return False

        params.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_product(self, product_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM order_items WHERE product_id = ?", (product_id,))
        usage_count = cursor.fetchone()[0]

        if usage_count > 0:
            conn.close()
            return False, "Нельзя удалить товар, который используется в заказах"

        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success, "Товар удален" if success else "Товар не найден"

    # Операции с заказами
    def create_order(self, customer_id, products):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if not cursor.fetchone():
            conn.close()
            return None, "Клиент не найден"

        total_amount = 0
        for product in products:
            cursor.execute("SELECT price, quantity FROM products WHERE id = ?", (product['product_id'],))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return None, f"Товар с ID {product['product_id']} не найден"

            price, available_quantity = result
            if product['quantity'] > available_quantity:
                conn.close()
                return None, f"Недостаточно товара с ID {product['product_id']}. Доступно: {available_quantity}"

            total_amount += price * product['quantity']

        cursor.execute(
            "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)",
            (customer_id, total_amount, 'pending')
        )
        order_id = cursor.lastrowid

        for product in products:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                (order_id, product['product_id'], product['quantity'])
            )

            cursor.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                (product['quantity'], product['product_id'])
            )

        conn.commit()
        conn.close()
        return order_id, "Заказ успешно создан"

    def get_all_orders(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT o.id, o.customer_id, o.total_amount, o.status, o.created_date,
                   c.name as customer_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.created_date DESC
        ''')

        orders = []
        for row in cursor.fetchall():
            cursor.execute('''
                SELECT p.name, oi.quantity, p.price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            ''', (row[0],))

            products = []
            for item_row in cursor.fetchall():
                products.append({
                    'name': item_row[0],
                    'quantity': item_row[1],
                    'price': item_row[2]
                })

            order_info = {
                'id': row[0],
                'customer_id': row[1],
                'total_amount': row[2],
                'status': row[3],
                'created_date': row[4],
                'customer_name': row[5],
                'products': products
            }
            orders.append(order_info)

        conn.close()
        return orders

    def get_orders_by_customer(self, customer_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT o.id, o.total_amount, o.status, o.created_date,
                   c.name, c.email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.customer_id = ?
        ''', (customer_id,))

        orders = []
        for row in cursor.fetchall():
            order = {
                'id': row[0],
                'total_amount': row[1],
                'status': row[2],
                'created_date': row[3],
                'customer_name': row[4],
                'customer_email': row[5]
            }
            orders.append(order)

        conn.close()
        return orders

    def update_order_status(self, order_id, status):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_order(self, order_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = ?", (order_id,))
            items = cursor.fetchall()

            for product_id, quantity in items:
                cursor.execute(
                    "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                    (quantity, product_id)
                )

            cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))

            conn.commit()
            success = cursor.rowcount > 0
            return success, "Заказ удален" if success else "Заказ не найден"
        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при удалении заказа: {str(e)}"
        finally:
            conn.close()

    # ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ - Аналитические функции
    def get_popular_products(self, limit=5):
        """Самые популярные товары"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.name, SUM(oi.quantity) as total_sold
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.id, p.name
            ORDER BY total_sold DESC
            LIMIT ?
        ''', (limit,))

        popular_products = cursor.fetchall()
        conn.close()
        return popular_products

    def get_average_order_value(self):
        """Средний чек заказов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT AVG(total_amount) FROM orders WHERE status != 'cancelled'")
        result = cursor.fetchone()
        avg_value = result[0] if result[0] else 0
        conn.close()
        return avg_value

    def get_total_revenue(self):
        """Общая выручка"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status = 'completed'")
        result = cursor.fetchone()
        total_revenue = result[0] if result[0] else 0
        conn.close()
        return total_revenue

    def get_orders_count(self):
        """Общее количество заказов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders")
        result = cursor.fetchone()
        count = result[0] if result[0] else 0
        conn.close()
        return count

    def get_customers_count(self):
        """Общее количество клиентов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM customers")
        result = cursor.fetchone()
        count = result[0] if result[0] else 0
        conn.close()
        return count

    def get_products_count(self):
        """Общее количество товаров"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        result = cursor.fetchone()
        count = result[0] if result[0] else 0
        conn.close()
        return count

    def get_best_customer(self):
        """Лучший клиент по сумме заказов"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.name, SUM(o.total_amount) as total_spent
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.status = 'completed'
            GROUP BY c.id, c.name
            ORDER BY total_spent DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()
        return result if result else ("Нет данных", 0)

    def get_orders_by_month(self):
        """Количество заказов по месяцам"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                strftime('%Y-%m', created_date) as month,
                COUNT(*) as order_count
            FROM orders
            GROUP BY month
            ORDER BY month
        ''')

        monthly_orders = cursor.fetchall()
        conn.close()
        return monthly_orders

    def get_revenue_by_month(self):
        """Выручка по месяцам"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                strftime('%Y-%m', created_date) as month,
                SUM(total_amount) as monthly_revenue
            FROM orders
            WHERE status = 'completed'
            GROUP BY month
            ORDER BY month
        ''')

        monthly_revenue = cursor.fetchall()
        conn.close()
        return monthly_revenue

    def clear_database(self):
        """Полная очистка базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Отключаем foreign keys для очистки
            cursor.execute("PRAGMA foreign_keys = OFF")

            # Очищаем таблицы в правильном порядке
            cursor.execute("DELETE FROM order_items")
            cursor.execute("DELETE FROM orders")
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM customers")

            # Сбрасываем автоинкремент
            cursor.execute("DELETE FROM sqlite_sequence")

            # Включаем foreign keys обратно
            cursor.execute("PRAGMA foreign_keys = ON")

            conn.commit()
            return True, "База данных успешно очищена"
        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при очистке базы данных: {str(e)}"
        finally:
            conn.close()

    def fill_test_data(self):
        """Заполнение тестовыми данными"""
        try:
            # Добавляем клиентов
            customers = [
                ("Иван Иванов", "ivan@mail.ru", "+79161234567"),
                ("Петр Петров", "petr@mail.ru", "+79167654321"),
                ("Мария Сидорова", "maria@mail.ru", "+79169998877"),
                ("Анна Козлова", "anna@mail.ru", "+79165554433"),
                ("Сергей Смирнов", "sergey@mail.ru", "+79167776655")
            ]

            customer_ids = []
            for customer in customers:
                customer_id = self.add_customer(*customer)
                if customer_id:
                    customer_ids.append(customer_id)

            # Добавляем товары
            products = [
                ("Ноутбук HP", 50000, 10),
                ("Мышь беспроводная", 1500, 50),
                ("Клавиатура механическая", 7000, 20),
                ("Монитор 24'", 15000, 15),
                ("Наушники Sony", 8000, 30),
                ("Веб-камера", 3000, 25),
                ("Микрофон", 4500, 15),
                ("Коврик для мыши", 500, 100)
            ]

            product_ids = []
            for product in products:
                product_id = self.add_product(*product)
                if product_id:
                    product_ids.append(product_id)

            # Создаем заказы
            import random
            orders_data = []
            for i in range(20):
                customer_id = random.choice(customer_ids)
                num_products = random.randint(1, 4)
                products_list = []
                for j in range(num_products):
                    product_id = random.choice(product_ids)
                    quantity = random.randint(1, 3)
                    products_list.append({'product_id': product_id, 'quantity': quantity})
                orders_data.append((customer_id, products_list))

            for customer_id, products in orders_data:
                self.create_order(customer_id, products)

            # Обновляем некоторые заказы в статус completed
            for i in range(1, 16):
                if random.random() > 0.3:  # 70% заказов completed
                    self.update_order_status(i, 'completed')

            return True, f"Добавлено: {len(customer_ids)} клиентов, {len(product_ids)} товаров, {len(orders_data)} заказов"

        except Exception as e:
            return False, f"Ошибка при заполнении тестовыми данными: {str(e)}"