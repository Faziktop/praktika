from console_crud import ConsoleCRUDInterface


def main():
    print("=== СИСТЕМА УЧЕТА ЗАКАЗОВ - УПРАВЛЕНИЕ ===")
    print("Версия 1: CRUD операции (добавление, редактирование, удаление)")

    interface = ConsoleCRUDInterface()
    interface.run()


if __name__ == "__main__":
    main()