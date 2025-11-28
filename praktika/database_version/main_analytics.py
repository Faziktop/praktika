from console_analytics import ConsoleAnalyticsInterface


def main():
    print("=== СИСТЕМА УЧЕТА ЗАКАЗОВ - АНАЛИТИКА ===")
    print("Версия 2: Вычислительный эксперимент (аналитика и отчеты)")

    interface = ConsoleAnalyticsInterface()
    interface.run()


if __name__ == "__main__":
    main()