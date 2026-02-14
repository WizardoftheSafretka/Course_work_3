import psycopg2


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных."""

    # Создаем копию params для подключения к стандартной БД
    conn_params = params.copy()
    # Устанавливаем кодировку для подключения
    conn_params['client_encoding'] = 'UTF8'

    # Подключаемся к стандартной базе данных (обычно postgres)
    conn = psycopg2.connect(dbname="postgres", **conn_params)
    conn.autocommit = True
    cur = conn.cursor()

    # Закрываем все соединения с базой данных, если она существует
    cur.execute(f"""
          SELECT pg_terminate_backend(pg_stat_activity.pid)
          FROM pg_stat_activity
          WHERE pg_stat_activity.datname = '{database_name}'
          AND pid <> pg_backend_pid();
      """)

    # Удаляем базу данных, если она существует (опционально)
    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cur.execute(f"CREATE DATABASE {database_name} ENCODING 'UTF8'")

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id int PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url text NOT NULL
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id int PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                salary float,
                url text NOT NULL,
                description text,
                employer_id INT REFERENCES employers(employer_id)
            )
        """)

    conn.commit()
    cur.close()
    conn.close()