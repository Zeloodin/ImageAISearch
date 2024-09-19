""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

# Импортируем модули, необходимые для работы с файлами и для работы с библиотекой Pickle
from os.path import isfile
import pickle as pk

from core.tools.variables import PKL_FILE_PATH, TEMP_VAL, EMPTY_LIST


def load_pkl(filename: (str, list) = PKL_FILE_PATH, temp_pkl: (list, str) = TEMP_VAL) -> list:
    """
    Функция `load_pkl` предназначена для загрузки данных из файла в формате `.pkl`или
    из списка, если файл не найден.

    Она принимает два параметра: `filename` и `temp_pkl`.
    Параметр `filename` может быть либо путём к файлу `.pkl`, либо списком данных, если файл отсутствует.
    Параметр `temp_pkl` представляет собой список данных, который используется, если `filename` не предоставлен.

    Функция возвращает список данных, загруженных из файла или списка.

    :param filename: Путь к файлу, для загрузки .pkl, или список данных, если файл отсутствует
    :param temp_pkl: Список pkl, если отсутствует filename,
    :return: возвращает список pkl
    """
    # Инициализируем переменную для хранения всех изображений
    all_image_features = EMPTY_LIST

    # Проверяем тип переданных параметров
    # Проверяем типы аргументов filename и temp_pkl
    filename = filename if isinstance(filename, (str, list)) else PKL_FILE_PATH
    temp_pkl = temp_pkl if isinstance(temp_pkl, (str, list)) else TEMP_VAL


    # Проверяем типы и значения параметров и выполняем соответствующие действия
    # Если filename - строка, а temp_pkl - список, проверяем наличие файла
    if isinstance(filename, str) and isinstance(temp_pkl, list):
        if isfile(filename):
            print(filename)
            # Загружаем данные из файла, если он существует
            all_image_features = pk.load(open(filename, "rb"))
        else:
            print(temp_pkl)
            # Используем список данных, если файл не найден
            all_image_features = temp_pkl
            print(f"file not found: {filename}")

    # Если filename - список, а temp_pkl - строка, проверяем наличие файла
    elif isinstance(filename, list) and isinstance(temp_pkl, str):
        if isfile(temp_pkl):
            print(temp_pkl)
            # Загружаем данные из файла, если он существует
            all_image_features = pk.load(open(temp_pkl, "rb"))
        else:
            print(filename)
            # Используем список данных, если файл не найден
            all_image_features = filename
            print(f"file not found: {filename}")

    # Если оба аргумента - строки, проверяем наличие файла
    elif isinstance(filename, str) and isinstance(temp_pkl, str):
        if isfile(filename):
            print(filename)
            # Загружаем данные из файла, если он существует
            all_image_features = pk.load(open(filename, "rb"))
        else:
            print(f"file not found: {filename}")
            print(temp_pkl)
            if isfile(temp_pkl):
                # Загружаем данные из файла, если он существует
                all_image_features = pk.load(open(temp_pkl, "rb"))
            else:
                print(f"file not found: {temp_pkl}")

    # Если оба аргумента - списки, выбираем первый непустой список
    elif isinstance(filename, list) and isinstance(temp_pkl, list):
        if len(filename) > 0:
            # Используем список данных, если он не пустой
            all_image_features = filename
        else:
            if len(temp_pkl) > 0:
                # Используем список данных, если он не пустой
                all_image_features = temp_pkl

    return all_image_features