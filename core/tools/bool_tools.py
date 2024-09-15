from typing import List, Optional, Union
# Импортируем необходимые типы данных для работы функции

from core.tools.list_tools import remove_duplicates as remdub
# Импортируем функцию `remove_duplicates` из модуля `core.tools.list_tools`
# и переименовываем её в `remdub` для удобства использования

def filter_bool(value: Union[bool, str, int, float] = False) -> bool:
    # Функция `filter_bool` принимает значение типа `Union[bool, str, int, float]`
    # и возвращает булево значение
    """
    Функция для проверки на буленновское значение.

    value: булеан или строка или целое число или вещественное число для фильтрации.
    """

    def _in_int(value: int):
        # Внутренняя функция `_in_int` используется
        # для преобразования значения в целое число и проверки его существования
        return int(value)  # Целое число -> bool

    def _in_float(value: float):
        # Внутренняя функция `_in_float` используется
        # для преобразования значения в вещественное число и проверки его на истинность
        if float(value) > 0.5:
            return True  # Вещественное число -> bool
        else:
            return False  # Вещественное число -> bool

    def _in_bool(value: bool):
        # Внутренняя функция `_in_bool` используется
        # для преобразования значения в булево и проверки его на истинность
        return bool(value)  # Целое число -> bool

    if isinstance(value, bool) and not isinstance(value, str):
        # Проверяем, является ли значение булевым и не является ли оно строкой
        return bool(_in_bool(bool(value)))

    elif isinstance(value, int) and not isinstance(value, str):
        # Проверяем, является ли значение целым числом и не является ли оно строкой
        return bool(_in_int(int(value)))

    elif isinstance(value, float) and not isinstance(value, str):
        # Проверяем, является ли значение вещественным числом и не является ли оно строкой
        return bool(_in_float(float(value)))

    elif isinstance(value, str):
        val1 = remdub(value, "lower", reverse=False, ext="str").capitalize()
        val2 = remdub(value, "lower", reverse=True, ext="str").capitalize()

        if value.isdigit():
            # Проверяем, является ли строка числом
            return bool(int(value))  # Целое число -> bool

        elif isfloat(value):
            # Проверяем, является ли строка вещественным числом
            if float(value) > 0.5:
                return True  # Вещественное число -> bool
            else:
                return False  # Вещественное число -> bool

        elif val1 == "True" or  val2 == "True":
            # Проверяем, соответствует ли строка значению "True"
            return True  # Бинарное, Двоичное, Булеан, Логический -> bool
        elif val1 == "False" or  val2 == "False":
            # Проверяем, соответствует ли строка значению "False"
            return False  # Бинарное, Двоичное, Булеан, Логический -> bool
    else:
        # Если значение не соответствует ни одному из условий, возвращаем False
        # print("Значение должно быть, bool")
        return False

def isfloat(value):
    # Вспомогательная функция для проверки, является ли строка вещественным числом
    if isinstance(value,str) and \
        value.count(".") <= 1 and \
        value.replace('.', '', 1).isdigit():
        return True
    return False