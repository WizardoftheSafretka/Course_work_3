import time
from typing import Optional

from src.DBManager import DBManager


def main():
    """
    Основная функция взаимодействия с пользователем.
    Предоставляет удобное меню для работы с базой данных вакансий.
    """

    # Параметры подключения к БД (можно вынести в конфиг или запрашивать у пользователя)
    params = {
        'host': 'localhost',
        'user': 'postgres',
        'password': 'your_password',
        'port': '5432'
    }
    database_name = 'hh_vacancies'

    print("=" * 60)
    print("ПРОГРАММА УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ ВАКАНСИЙ")
    print("=" * 60)

    # Подключаемся к БД
    try:
        db_manager = DBManager(database_name, params)
        print("✓ Подключение к базе данных установлено")
    except Exception as e:
        print(f"✗ Ошибка подключения к базе данных: {e}")
        print("Проверьте параметры подключения и наличие базы данных")
        return

    while True:
        print("\n" + "-" * 60)
        print("ДОСТУПНЫЕ ОПЕРАЦИИ:")
        print("1. Показать список компаний и количество вакансий")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату по всем вакансиям")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("6. Показать статистику по базе данных")
        print("0. Выход")
        print("-" * 60)

        choice = input("Выберите действие (0-6): ").strip()

        if choice == '0':
            print("\nЗавершение работы программы...")
            db_manager.close()
            print("До свидания!")
            break

        elif choice == '1':
            display_companies_and_vacancies(db_manager)

        elif choice == '2':
            display_all_vacancies(db_manager)

        elif choice == '3':
            display_avg_salary(db_manager)

        elif choice == '4':
            display_vacancies_higher_salary(db_manager)

        elif choice == '5':
            search_vacancies_by_keyword(db_manager)

        elif choice == '6':
            display_statistics(db_manager)

        else:
            print("✗ Неверный ввод. Пожалуйста, выберите действие от 0 до 6.")

        input("\nНажмите Enter для продолжения...")


def display_companies_and_vacancies(db_manager: DBManager) -> None:
    """
    Отображает список компаний и количество вакансий у каждой.
    """
    print("\n" + "=" * 60)
    print("КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 60)

    companies = db_manager.get_companies_and_vacancies_count()

    if not companies:
        print("В базе данных нет информации о компаниях.")
        return

    print(f"\nНайдено компаний: {len(companies)}")
    print("\nСписок компаний:")
    print("-" * 60)

    for i, company in enumerate(companies, 1):
        company_name = company['company_name']
        vacancies_count = company['vacancies_count']

        # Формируем строку с информацией о количестве вакансий
        if vacancies_count == 0:
            vacancies_info = "нет открытых вакансий"
        elif vacancies_count == 1:
            vacancies_info = "1 вакансия"
        elif 2 <= vacancies_count <= 4:
            vacancies_info = f"{vacancies_count} вакансии"
        else:
            vacancies_info = f"{vacancies_count} вакансий"

        print(f"{i:2}. {company_name} — {vacancies_info}")


def display_all_vacancies(db_manager: DBManager) -> None:
    """
    Отображает все вакансии с подробной информацией.
    """
    print("\n" + "=" * 60)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 60)

    vacancies = db_manager.get_all_vacancies()

    if not vacancies:
        print("В базе данных нет информации о вакансиях.")
        return

    print(f"\nВсего вакансий: {len(vacancies)}")
    print("\nСписок вакансий:")
    print("-" * 60)

    current_company = None
    vacancy_counter = 0

    for vacancy in vacancies:
        company_name = vacancy['company_name']

        # Если сменилась компания, выводим заголовок
        if company_name != current_company:
            current_company = company_name
            vacancy_counter = 1
            print(f"\n🏢 {company_name.upper()}:")

        # Форматируем зарплату
        salary = vacancy['salary']
        if salary and salary > 0:
            if salary.is_integer():
                salary_str = f"{int(salary):,} руб.".replace(",", " ")
            else:
                salary_str = f"{salary:,.2f} руб.".replace(",", " ")
        else:
            salary_str = "зарплата не указана"

        # Выводим информацию о вакансии
        print(f"  {vacancy_counter:2}. {vacancy['vacancy_name']}")
        print(f"     💰 {salary_str}")
        print(f"     🔗 {vacancy['vacancy_url']}")

        vacancy_counter += 1


def display_avg_salary(db_manager: DBManager) -> None:
    """
    Отображает среднюю зарплату по всем вакансиям.
    """
    print("\n" + "=" * 60)
    print("СРЕДНЯЯ ЗАРПЛАТА")
    print("=" * 60)

    avg_salary = db_manager.get_avg_salary()

    if avg_salary > 0:
        # Форматируем для красивого отображения
        if avg_salary.is_integer():
            salary_str = f"{int(avg_salary):,}".replace(",", " ")
        else:
            salary_str = f"{avg_salary:,.2f}".replace(",", " ")

        print(f"\n💰 Средняя зарплата по всем вакансиям: {salary_str} руб.")

        # Добавляем контекст
        if avg_salary < 50000:
            print("   (относительно невысокий уровень зарплат)")
        elif avg_salary < 100000:
            print("   (средний уровень зарплат)")
        elif avg_salary < 150000:
            print("   (выше среднего уровень зарплат)")
        else:
            print("   (высокий уровень зарплат)")
    else:
        print("\nНедостаточно данных для расчета средней зарплаты.")
        print("Возможно, в базе нет вакансий с указанной зарплатой.")


def display_vacancies_higher_salary(db_manager: DBManager) -> None:
    """
    Отображает вакансии с зарплатой выше средней.
    """
    print("\n" + "=" * 60)
    print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
    print("=" * 60)

    # Сначала получаем среднюю зарплату
    avg_salary = db_manager.get_avg_salary()

    if avg_salary == 0:
        print("\nНевозможно определить вакансии с зарплатой выше средней.")
        print("Причина: отсутствуют данные о зарплатах.")
        return

    vacancies = db_manager.get_vacancies_with_higher_salary()

    if not vacancies:
        print(f"\nНет вакансий с зарплатой выше средней ({avg_salary:,.2f} руб.)")
        return

    # Форматируем среднюю зарплату для отображения
    if avg_salary.is_integer():
        avg_salary_str = f"{int(avg_salary):,}".replace(",", " ")
    else:
        avg_salary_str = f"{avg_salary:,.2f}".replace(",", " ")

    print(f"\nСредняя зарплата по всем вакансиям: {avg_salary_str} руб.")
    print(f"Найдено вакансий с зарплатой выше средней: {len(vacancies)}")
    print("\nСписок вакансий (отсортирован по убыванию зарплаты):")
    print("-" * 60)

    for i, vacancy in enumerate(vacancies, 1):
        # Форматируем зарплату
        salary = vacancy['salary']
        if salary and salary > 0:
            if salary.is_integer():
                salary_str = f"{int(salary):,} руб.".replace(",", " ")
            else:
                salary_str = f"{salary:,.2f} руб.".replace(",", " ")

            # Рассчитываем процент превышения
            percent_above = ((salary - avg_salary) / avg_salary) * 100
            percent_str = f"(+{percent_above:.1f}%)"
        else:
            salary_str = "зарплата не указана"
            percent_str = ""

        print(f"\n{i}. {vacancy['vacancy_name']}")
        print(f"   Компания: {vacancy['company_name']}")
        print(f"   Зарплата: {salary_str} {percent_str}")
        print(f"   Ссылка: {vacancy['vacancy_url']}")

        # Показываем описание, если оно есть
        if vacancy.get('description'):
            description = vacancy['description']
            if len(description) > 100:
                description = description[:100] + "..."
            print(f"   Описание: {description}")


def search_vacancies_by_keyword(db_manager: DBManager) -> None:
    """
    Поиск вакансий по ключевому слову.
    """
    print("\n" + "=" * 60)
    print("ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВОМУ СЛОВУ")
    print("=" * 60)

    keyword = input("\nВведите ключевое слово для поиска: ").strip()

    if not keyword:
        print("✗ Ключевое слово не может быть пустым.")
        return

    print(f"\nИщем вакансии, содержащие '{keyword}' в названии...")
    time.sleep(0.5)  # Небольшая задержка для имитации поиска

    vacancies = db_manager.get_vacancies_with_keyword(keyword)

    if not vacancies:
        print(f"\nПо запросу '{keyword}' ничего не найдено.")
        print("Попробуйте изменить ключевое слово или использовать менее специфичный запрос.")
        return

    print(f"\nПо запросу '{keyword}' найдено вакансий: {len(vacancies)}")
    print("\nРезультаты поиска:")
    print("-" * 60)

    # Группируем результаты по компаниям
    companies_vacancies = {}
    for vacancy in vacancies:
        company = vacancy['company_name']
        if company not in companies_vacancies:
            companies_vacancies[company] = []
        companies_vacancies[company].append(vacancy)

    for company, company_vacancies in companies_vacancies.items():
        print(f"\n🏢 {company}:")

        for i, vacancy in enumerate(company_vacancies, 1):
            # Форматируем зарплату
            salary = vacancy['salary']
            if salary and salary > 0:
                if salary.is_integer():
                    salary_str = f"{int(salary):,} руб.".replace(",", " ")
                else:
                    salary_str = f"{salary:,.2f} руб.".replace(",", " ")
            else:
                salary_str = "зарплата не указана"

            print(f"  {i}. {vacancy['vacancy_name']}")
            print(f"     💰 {salary_str}")
            print(f"     🔗 {vacancy['vacancy_url']}")


def display_statistics(db_manager: DBManager) -> None:
    """
    Отображает общую статистику по базе данных.
    """
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПО БАЗЕ ДАННЫХ")
    print("=" * 60)

    stats = db_manager.get_statistics_summary()

    if not stats:
        print("Не удалось получить статистику.")
        return

    total_companies = stats.get('total_companies', 0)
    total_vacancies = stats.get('total_vacancies', 0)
    avg_salary = stats.get('avg_salary', 0)
    min_salary = stats.get('min_salary', 0)
    max_salary = stats.get('max_salary', 0)
    vacancies_with_salary = stats.get('vacancies_with_salary', 0)

    print(f"\n📊 Общая информация:")
    print(f"   • Компаний в базе: {total_companies}")
    print(f"   • Всего вакансий: {total_vacancies}")
    print(f"   • Вакансий с указанной зарплатой: {vacancies_with_salary}")

    if total_vacancies > 0:
        # Процент вакансий с зарплатой
        if total_vacancies > 0:
            percent_with_salary = (vacancies_with_salary / total_vacancies) * 100
            print(f"   • Вакансий с зарплатой: {percent_with_salary:.1f}%")

    print(f"\n💰 Информация о зарплатах:")
    if vacancies_with_salary > 0:
        # Форматируем зарплаты
        if avg_salary and avg_salary > 0:
            avg_salary_str = f"{avg_salary:,.2f}".replace(",", " ") if avg_salary else "нет данных"
            print(f"   • Средняя зарплата: {avg_salary_str} руб.")

        if min_salary and min_salary > 0:
            min_salary_str = f"{min_salary:,.2f}".replace(",", " ") if min_salary else "нет данных"
            print(f"   • Минимальная зарплата: {min_salary_str} руб.")

        if max_salary and max_salary > 0:
            max_salary_str = f"{max_salary:,.2f}".replace(",", " ") if max_salary else "нет данных"
            print(f"   • Максимальная зарплата: {max_salary_str} руб.")

        # Разброс зарплат
        if min_salary and max_salary and max_salary > min_salary:
            spread = max_salary - min_salary
            spread_str = f"{spread:,.2f}".replace(",", " ")
            print(f"   • Разброс зарплат: {spread_str} руб.")
    else:
        print("   • Нет данных о зарплатах в базе")


if __name__ == "__main__":
    main()