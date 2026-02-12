from abc import ABC, abstractmethod

import requests


class Parser(ABC):
    """
    Абстрактный класс Parser
    """

    @abstractmethod
    def _api_connection(self):
        """Абстрактный метод подключения к API"""

        pass


class HeadHunterAPI(Parser):
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self):
        """Инициализация класса HH"""
        self._url = "https://api.hh.ru/employers/"
        self._headers = {"User-Agent": "HH-User-Agent"}
        self._params = {"page": 0, "per_page": 1}
        self._employers = []
        self._companies_ids = [
            "1122462", "15478", "9694561", "1942336", "2671",
            "3529", "3776", "78638", "10317521", "1035394"
        ]

    def _api_connection(self):
        """Метод подключения к API и получения данных о работодателях"""
        self._employers.clear()

        for comp_id in self._companies_ids:
            try:
                response = requests.get(self._url + comp_id, headers=self._headers)
                response.raise_for_status()

                employer_data = response.json()
                self._employers.append(employer_data)
                print(f"Получены данные о компании: {employer_data.get('name')}")

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении данных о компании {comp_id}: {e}")

        return self._employers

    def get_employer_vacancies(self, employer_id):
        """Получение вакансий конкретного работодателя"""
        vacancies_url = f"https://api.hh.ru/vacancies/?employer_id={employer_id}"
        params = {"page": 0, "per_page": 100}
        all_vacancies = []

        try:
                response = requests.get(vacancies_url, headers=self._headers, params=params)
                response.raise_for_status()

                data = response.json()
                vacancies = data.get("items", [])
                all_vacancies.extend(vacancies)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий для компании {employer_id}: {e}")

        return all_vacancies

    def get_all_employers_with_vacancies(self):
        """Получение всех работодателей с их вакансиями"""
        employers_data = []

        employers = self._api_connection()

        for employer in employers:
            employer_id = employer.get("id")
            vacancies = self.get_employer_vacancies(employer_id)

            employers_data.append({
                "employer": employer,
                "vacancies": vacancies,
                "vacancies_count": len(vacancies)
            })

            print(f"Для компании {employer.get('name')} получено {len(vacancies)} вакансий")

        return employers_data

# Создание экземпляра класса
hh_api = HeadHunterAPI()

# Получение всех работодателей с вакансиями
all_data = hh_api.get_all_employers_with_vacancies()

# # Или поэтапно:
# employers = hh_api._api_connection()
# for employer in employers:
#     vacancies = hh_api.get_employer_vacancies(employer["id"])
#     print(f"{employer['name']}: {len(vacancies)} вакансий")