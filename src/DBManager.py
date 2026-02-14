import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Tuple, Optional, Any


class DBManager:
    """
    Класс для управления базой данных с информацией о компаниях и вакансиях.
    Предоставляет методы для получения различных статистических данных.
    """

    def __init__(self, database_name: str, params: dict):
        """
        Инициализация подключения к базе данных.

        Args:
            database_name: Имя базы данных
            params: Параметры подключения (host, user, password, port)
        """
        self.database_name = database_name
        self.params = params.copy()
        self.params['client_encoding'] = 'UTF8'
        self.conn = None

    def __enter__(self):
        """Контекстный менеджер для автоматического открытия соединения"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер для автоматического закрытия соединения"""
        self.close()

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.conn = psycopg2.connect(
                dbname=self.database_name,
                **self.params
            )
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[dict]]:
        """
        Внутренний метод для выполнения SQL запросов.

        Args:
            query: SQL запрос
            params: Параметры запроса
            fetch: Нужно ли возвращать результаты

        Returns:
            Список словарей с результатами запроса или None
        """
        if not self.conn:
            self.connect()

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                self.conn.commit()
                return None
        except psycopg2.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            if params:
                print(f"Параметры: {params}")
            self.conn.rollback()
            return None if fetch else None

    def get_companies_and_vacancies_count(self) -> List[dict]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            Список словарей с полями: company_name, vacancies_count
        """
        query = """
            SELECT 
                e.name AS company_name,
                COUNT(v.vacancy_id) AS vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.employer_id, e.name
            ORDER BY vacancies_count DESC, e.name
        """

        result = self._execute_query(query)
        return result if result else []

    def get_all_vacancies(self) -> List[dict]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Returns:
            Список словарей с полями: company_name, vacancy_name, salary, vacancy_url
        """
        query = """
            SELECT 
                e.name AS company_name,
                v.name AS vacancy_name,
                v.salary,
                v.url AS vacancy_url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.name, v.salary DESC NULLS LAST
        """

        result = self._execute_query(query)
        return result if result else []

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            Средняя зарплата (float)
        """
        query = """
            SELECT ROUND(AVG(salary), 2) as avg_salary
            FROM vacancies
            WHERE salary > 0
        """

        result = self._execute_query(query)
        if result and result[0]['avg_salary']:
            return float(result[0]['avg_salary'])
        return 0.0

    def get_vacancies_with_higher_salary(self) -> List[dict]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            Список словарей с информацией о вакансиях
        """
        query = """
            SELECT 
                v.vacancy_id,
                v.name AS vacancy_name,
                e.name AS company_name,
                v.salary,
                v.url AS vacancy_url,
                v.description
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE v.salary > (SELECT AVG(salary) FROM vacancies WHERE salary > 0)
            ORDER BY v.salary DESC
        """

        result = self._execute_query(query)
        return result if result else []

    def get_vacancies_with_keyword(self, keyword: str) -> List[dict]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова.

        Args:
            keyword: Ключевое слово для поиска в названии вакансии

        Returns:
            Список словарей с информацией о вакансиях
        """
        # Разбиваем ключевое слово на отдельные слова для более гибкого поиска
        words = keyword.lower().split()

        # Строим условие для поиска любого из слов в названии
        conditions = []
        params = []

        for word in words:
            conditions.append("LOWER(v.name) LIKE %s")
            params.append(f'%{word}%')

        where_clause = " OR ".join(conditions) if conditions else "TRUE"

        query = f"""
            SELECT 
                v.vacancy_id,
                v.name AS vacancy_name,
                e.name AS company_name,
                v.salary,
                v.url AS vacancy_url,
                v.description
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE {where_clause}
            ORDER BY e.name, v.salary DESC NULLS LAST
        """

        result = self._execute_query(query, tuple(params) if params else None)
        return result if result else []