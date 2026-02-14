from typing import Any

import psycopg2

from src.utils import salary


def save_data_to_database_employers(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о каналах и видео в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in data:
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, url)
                VALUES (%s, %s, %s)
                RETURNING employer_id
                """,
                (employer['id'], employer['name'], employer['alternate_url'],
                 )
            )
    conn.commit()
    conn.close()


def save_data_to_database_vacancies(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Сохранение данных о вакансиях в базу данных."""

    conn_params = params.copy()
    conn_params['client_encoding'] = 'UTF8'
    conn = psycopg2.connect(dbname=database_name, **conn_params)

    with conn.cursor() as cur:
        for vacancy in data:
            try:
                # Безопасное получение данных
                vacancy_id = int(vacancy['id'])  # Преобразуем в int, так как в таблице int
                vacancy_name = vacancy['name']
                salary_value = salary(vacancy.get('salary'))
                vacancy_url = vacancy.get('alternate_url', '')

                # Получаем описание из snippet
                snippet = vacancy.get('snippet', {})
                description = snippet.get('responsibility') or snippet.get('requirement') or ''

                # Получаем employer_id
                employer = vacancy.get('employer', {})
                employer_id = int(employer.get('id', 0))

                cur.execute(
                    """
                    INSERT INTO vacancies (vacancy_id, name, salary, url, description, employer_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        vacancy_id,
                        vacancy_name,
                        salary_value,
                        vacancy_url,
                        description,
                        employer_id
                    )
                )
            except Exception as e:
                print(f"Ошибка при сохранении вакансии {vacancy.get('id', 'unknown')}: {e}")
                print(f"Данные вакансии: {vacancy}")
                continue

    conn.commit()
    conn.close()