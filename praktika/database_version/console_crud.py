from database import DatabaseManager


class ConsoleCRUDInterface:
    def __init__(self):
        self.db = DatabaseManager()

    def display_menu(self):
        print("\n=== СИСТЕМА УЧЕТА ЗАКАЗОВ - УПРАВЛЕНИЕ ===")
        print("1. Управление клиентами")
        print("2. Управление товарами")
        print("3. Управление заказами")
        print("4. Очистка базы данных")
        print("5. Заполнить тестовыми данными")
        print("0. Выход")

    def display_customers_menu(self):
        print("\n--- Управление клиентами ---")
        print("1. Показать всех клиентов")
        print("2. Добавить клиента")
        print("3. Найти клиента по ID")
        print("4. Редактировать клиента")
        print("5. Удалить клиента")
        print("0. Назад")

    def display_products_menu(self):
        print("\n--- Управление товарами ---")
        print("1. Показать все товары")
        print("2. Добавить товар")
        print("3. Найти товар по ID")
        print("4. Редактировать товар")
        print("5. Удалить товар")
        print("0. Назад")

    def display_orders_menu(self):
        print("\n--- Управление заказами ---")
        print("1. Показать все заказы")
        print("2. Создать заказ")
        print("3. Заказы клиента")
        print("4. Изменить статус заказа")
        print("5. Удалить заказ")
        print("0. Назад")

    def run(self):
        while True:
            self.display_menu()
            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.manage_customers()
            elif choice == '2':
                self.manage_products()
            elif choice == '3':
                self.manage_orders()
            elif choice == '4':
                self.clear_database()
            elif choice == '5':
                self.fill_test_data()
            elif choice == '0':
                print("Выход из программы...")
                break
            else:
                print("Неверный выбор!")

    def manage_customers(self):
        while True:
            self.display_customers_menu()
            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.show_all_customers()
            elif choice == '2':
                self.add_customer()
            elif choice == '3':
                self.find_customer_by_id()
            elif choice == '4':
                self.update_customer()
            elif choice == '5':
                self.delete_customer()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")

    def show_all_customers(self):
        customers = self.db.get_all_customers()
        if not customers:
            print("Клиенты не найдены.")
            return

        print("\n--- Все клиенты ---")
        for customer in customers:
            print(f"ID: {customer.id}, Имя: {customer.name}, Email: {customer.email}, Телефон: {customer.phone}")

    def add_customer(self):
        print("\n--- Добавление клиента ---")
        name = input("Имя: ").strip()
        email = input("Email: ").strip()
        phone = input("Телефон: ").strip()

        if not name or not email:
            print("Имя и email обязательны!")
            return

        customer_id = self.db.add_customer(name, email, phone)
        if customer_id:
            print(f"Клиент добавлен с ID: {customer_id}")
        else:
            print("Ошибка: клиент с таким email уже существует!")

    def find_customer_by_id(self):
        try:
            customer_id = int(input("Введите ID клиента: ").strip())
            customer = self.db.get_customer_by_id(customer_id)
            if customer:
                print(f"\nID: {customer.id}")
                print(f"Имя: {customer.name}")
                print(f"Email: {customer.email}")
                print(f"Телефон: {customer.phone}")
            else:
                print("Клиент не найден!")
        except ValueError:
            print("Неверный формат ID!")

    def update_customer(self):
        try:
            customer_id = int(input("Введите ID клиента для редактирования: ").strip())
            customer = self.db.get_customer_by_id(customer_id)
            if not customer:
                print("Клиент не найден!")
                return

            print(f"\nТекущие данные клиента:")
            print(f"Имя: {customer.name}")
            print(f"Email: {customer.email}")
            print(f"Телефон: {customer.phone}")

            print("\nВведите новые данные (оставьте пустым для сохранения текущего значения):")
            name = input(f"Новое имя [{customer.name}]: ").strip()
            email = input(f"Новый email [{customer.email}]: ").strip()
            phone = input(f"Новый телефон [{customer.phone}]: ").strip()

            name = name if name else None
            email = email if email else None
            phone = phone if phone else None

            success = self.db.update_customer(customer_id, name, email, phone)
            if success:
                print("Данные клиента обновлены!")
            else:
                print("Ошибка при обновлении данных!")
        except ValueError:
            print("Неверный формат ID!")

    def delete_customer(self):
        try:
            customer_id = int(input("Введите ID клиента для удаления: ").strip())
            success, message = self.db.delete_customer(customer_id)
            print(message)
        except ValueError:
            print("Неверный формат ID!")

    def manage_products(self):
        while True:
            self.display_products_menu()
            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.show_all_products()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.find_product_by_id()
            elif choice == '4':
                self.update_product()
            elif choice == '5':
                self.delete_product()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")

    def show_all_products(self):
        products = self.db.get_all_products()
        if not products:
            print("Товары не найдены.")
            return

        print("\n--- Все товары ---")
        for product in products:
            print(f"ID: {product.id}, Название: {product.name}, Цена: {product.price}, Кол-во: {product.quantity}")

    def add_product(self):
        print("\n--- Добавление товара ---")
        name = input("Название: ").strip()
        try:
            price = float(input("Цена: ").strip())
            quantity = int(input("Количество: ").strip())
        except ValueError:
            print("Неверный формат данных!")
            return

        if not name or price < 0 or quantity < 0:
            print("Некорректные данные!")
            return

        product_id = self.db.add_product(name, price, quantity)
        print(f"Товар добавлен с ID: {product_id}")

    def find_product_by_id(self):
        try:
            product_id = int(input("Введите ID товара: ").strip())
            product = self.db.get_product_by_id(product_id)
            if product:
                print(f"\nID: {product.id}")
                print(f"Название: {product.name}")
                print(f"Цена: {product.price}")
                print(f"Количество: {product.quantity}")
            else:
                print("Товар не найден!")
        except ValueError:
            print("Неверный формат ID!")

    def update_product(self):
        try:
            product_id = int(input("Введите ID товара для редактирования: ").strip())
            product = self.db.get_product_by_id(product_id)
            if not product:
                print("Товар не найден!")
                return

            print(f"\nТекущие данные товара:")
            print(f"Название: {product.name}")
            print(f"Цена: {product.price}")
            print(f"Количество: {product.quantity}")

            print("\nВведите новые данные (оставьте пустым для сохранения текущего значения):")
            name = input(f"Новое название [{product.name}]: ").strip()
            price_str = input(f"Новая цена [{product.price}]: ").strip()
            quantity_str = input(f"Новое количество [{product.quantity}]: ").strip()

            name = name if name else None
            price = float(price_str) if price_str else None
            quantity = int(quantity_str) if quantity_str else None

            success = self.db.update_product(product_id, name, price, quantity)
            if success:
                print("Данные товара обновлены!")
            else:
                print("Ошибка при обновлении данных!")
        except ValueError:
            print("Неверный формат данных!")

    def delete_product(self):
        try:
            product_id = int(input("Введите ID товара для удаления: ").strip())
            success, message = self.db.delete_product(product_id)
            print(message)
        except ValueError:
            print("Неверный формат ID!")

    def manage_orders(self):
        while True:
            self.display_orders_menu()
            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.show_all_orders()
            elif choice == '2':
                self.create_order()
            elif choice == '3':
                self.show_customer_orders()
            elif choice == '4':
                self.update_order_status()
            elif choice == '5':
                self.delete_order()
            elif choice == '0':
                break
            else:
                print("Неверный выбор!")

    def show_all_orders(self):
        orders = self.db.get_all_orders()
        if not orders:
            print("Заказы не найдены.")
            return

        print("\n--- Все заказы ---")
        for order in orders:
            print(f"\nЗаказ №{order['id']}")
            print(f"Клиент: {order['customer_name']} (ID: {order['customer_id']})")
            print(f"Сумма: {order['total_amount']}")
            print(f"Статус: {order['status']}")
            print(f"Дата: {order['created_date']}")
            print("Товары:")
            for product in order['products']:
                print(f"  - {product['name']}: {product['quantity']} шт. x {product['price']} руб.")

    def create_order(self):
        print("\n--- Создание заказа ---")

        customers = self.db.get_all_customers()
        if not customers:
            print("Нет клиентов для создания заказа!")
            return

        print("Доступные клиенты:")
        for customer in customers:
            print(f"ID: {customer.id}, Имя: {customer.name}")

        try:
            customer_id = int(input("Введите ID клиента: ").strip())
        except ValueError:
            print("Неверный формат ID!")
            return

        products = self.db.get_all_products()
        if not products:
            print("Нет товаров для заказа!")
            return

        print("\nДоступные товары:")
        for product in products:
            print(f"ID: {product.id}, Название: {product.name}, Цена: {product.price}, В наличии: {product.quantity}")

        order_products = []
        while True:
            try:
                product_id = int(input("Введите ID товара (0 для завершения): ").strip())
                if product_id == 0:
                    break

                quantity = int(input("Введите количество: ").strip())

                if quantity <= 0:
                    print("Количество должно быть положительным!")
                    continue

                order_products.append({'product_id': product_id, 'quantity': quantity})
                print("Товар добавлен в заказ")

            except ValueError:
                print("Неверный формат данных!")
                continue

        if not order_products:
            print("Заказ не может быть пустым!")
            return

        order_id, message = self.db.create_order(customer_id, order_products)
        print(message)
        if order_id:
            print(f"Заказ создан с номером: {order_id}")

    def show_customer_orders(self):
        try:
            customer_id = int(input("Введите ID клиента: ").strip())
            orders = self.db.get_orders_by_customer(customer_id)

            if not orders:
                print("Заказы не найдены.")
                return

            customer_name = orders[0]['customer_name'] if orders else "Неизвестный"
            print(f"\n--- Заказы клиента {customer_name} ---")
            for order in orders:
                print(
                    f"Заказ №{order['id']}: {order['total_amount']} руб. ({order['status']}) - {order['created_date']}")

        except ValueError:
            print("Неверный формат ID!")

    def update_order_status(self):
        try:
            order_id = int(input("Введите ID заказа: ").strip())
            print("Доступные статусы: pending, completed, cancelled")
            status = input("Новый статус: ").strip()

            if status not in ['pending', 'completed', 'cancelled']:
                print("Неверный статус!")
                return

            success = self.db.update_order_status(order_id, status)
            if success:
                print("Статус заказа обновлен!")
            else:
                print("Заказ не найден!")
        except ValueError:
            print("Неверный формат ID!")

    def delete_order(self):
        try:
            order_id = int(input("Введите ID заказа для удаления: ").strip())
            success, message = self.db.delete_order(order_id)
            print(message)
        except ValueError:
            print("Неверный формат ID!")

    def clear_database(self):
        print("\n--- Очистка базы данных ---")
        print("ВНИМАНИЕ: Это действие удалит все данные из базы данных!")
        confirmation = input("Вы уверены? (да/нет): ").strip().lower()

        if confirmation == 'да':
            success, message = self.db.clear_database()
            print(message)
        else:
            print("Очистка отменена.")

    def fill_test_data(self):
        print("\n--- Заполнение тестовыми данными ---")
        success, message = self.db.fill_test_data()
        print(message)