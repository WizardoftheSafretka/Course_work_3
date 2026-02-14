def salary(salary_data):
    """Валидация и вычисление зарплаты."""
    if not salary_data:
        return 0

    if isinstance(salary_data, dict):
        # Получаем значения from и to
        from_salary = salary_data.get("from")
        to_salary = salary_data.get("to")

        # Проверяем и преобразуем в числа
        from_salary = float(from_salary) if from_salary and isinstance(from_salary, (int, float)) else 0
        to_salary = float(to_salary) if to_salary and isinstance(to_salary, (int, float)) else 0

        if from_salary == 0 and to_salary == 0:
            return 0
        elif from_salary == 0:
            return to_salary
        elif to_salary == 0:
            return from_salary
        else:
            return (from_salary + to_salary) / 2
    elif isinstance(salary_data, (int, float)):
        return float(salary_data)
    else:
        return 0