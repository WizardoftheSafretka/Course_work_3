from abc import ABC, abstractmethod

import requests


class Parser(ABC):
    """
    Абстрактный класс Parser
    """

    @abstractmethod
    def get_employers(self):
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

    def get_employers(self):
        """Метод подключения к API и получения данных о работодателях"""
        self._employers.clear()

        for comp_id in self._companies_ids:
            try:
                response = requests.get(self._url + comp_id, headers=self._headers)
                response.raise_for_status()

                employer_data = response.json()
                self._employers.append(employer_data)

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении данных о компании {comp_id}: {e}")

        return self._employers

    def get_employer_vacancies(self):
        """Получение вакансий конкретного работодателя"""
        vacancies_url = f"https://api.hh.ru/vacancies/?employer_id="
        params = {"page": 0, "per_page": 100}
        all_vacancies = []

        for comp_id in self._companies_ids:
            try:
                    response = requests.get(vacancies_url + comp_id, headers=self._headers, params=params)
                    response.raise_for_status()

                    data = response.json()
                    vacancies = data.get("items", [])
                    all_vacancies.extend(vacancies)

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении вакансий: {e}")

        return all_vacancies
