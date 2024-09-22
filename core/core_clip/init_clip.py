""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

import os
import pathlib
from os import path
from os.path import isfile
from string import ascii_letters
from types import NoneType
from typing import List, Optional, Union

import numpy as np
import torch
import clip
import json
from PIL import Image
import pickle as pk
from tqdm import tqdm
from sklearn.neighbors import NearestNeighbors
import hnswlib
import re

from sklearn.utils._param_validation import InvalidParameterError

from keyboard import add_hotkey # В случае, когда надо отключить
import asyncio # Во время выполнения, асинхронно выполняет, рядом с другими задачами

from core.tools.list_tools import mini_translator
from core.tools.json_tools import load_json_file, save_json_file
from core.tools.bool_tools import filter_bool
from core.tools.folder_tools import Folder_make_list, isdir_makefolder, filter_str_list, search_in_list
from core.core_clip.load_clip import load_pkl
from core.core_clip.save_clip import save_pkl

from core.tools.variables import PKL_FILE_PATH, TEMP_VAL, CLIP_LOAD, EMPTY_LIST, PATH_SEARCH_RES, JSON_FILE_PATH



class Generate_clip_features:
    def __init__(self,
                 filename_pkl=PKL_FILE_PATH,
                 temp_pkl=TEMP_VAL,
                 folder_list: Union[List[str], str] = [],
                 neg_folder_list: Optional[Union[List[str], str]] = [],
                 white_list: Optional[Union[List[str], str]] = [],
                 black_list: Optional[Union[List[str], str]] = [],
                 filter_work: Optional[Union[bool, str, int, float]] = False,
                 append_white: Optional[Union[bool, str, int, float]] = False,
                 clip_load: str = CLIP_LOAD,
                 device = None):
        """
                `device` будет использоваться для определения устройства,
                на котором будут выполняться операции. cuda or cpu

                `model` будет хранить ссылку на модель CLIP,
                которая будет использоваться для извлечения векторных представлений

                `preprocess` будет хранить ссылку на предобработчик,
                который будет использоваться для подготовки изображений к работе с моделью CLIP.

                `save_every_n` будет использоваться для определения частоты сохранения результатов.


                `clip_load` будет использоваться для хранения пути к файлу,
                содержащему модель CLIP, которую необходимо загрузить.


                `filename_pkl` и `temp_pkl` будут использоваться для хранения путей к файлам,
                в которых будут сохраняться результаты работы программы.


                `all_image_features` будет использоваться
                для хранения векторных представлений всех обработанных изображений.


                `image_filenames` будет использоваться
                для хранения списка имен всех изображений, которые необходимо обработать.


                `folder_list`, `neg_folder_list`, `white_list`, `black_list`, `filter_work`, `append_white`
                будут использоваться для настройки параметров обработки изображений.


                `fol_mak_lis` будет использоваться для хранения экземпляра класса `Folder_make_list`,
                который будет использоваться для получения списка изображений для обработки.


                `fomali_get_values` будет использоваться
                для получения значений из экземпляра класса `Folder_make_list`.
                """
        # Инициализация переменных класса
        self.__device = device
        self.__model = None
        self.__preprocess = None
        self.__save_every_n = 0
        # self.__clip_load = None

        self.__fml = False

        # Установка значения для загрузки модели CLIP
        self.__clip_load = clip_load if clip_load != None else self.__folder_list

        # Инициализация переменных класса
        self.__filename_pkl = filename_pkl
        self.__temp_pkl = temp_pkl

        # Создание списка имен изображений
        self.__image_filenames = []

        # Инициализация других переменных класса
        self.__folder_list = folder_list
        self.__neg_folder_list = neg_folder_list
        self.__white_list = white_list
        self.__black_list = black_list
        self.__filter_work = filter_work
        self.__append_white = append_white


        self.__ex_return = False
        try:
            # Если Английская расскладка, то код будет выполниться правильно.
            add_hotkey("shift + `", lambda: asyncio.run(self.__exit_return_break("shift + `")))
        except ValueError:
            # Если Русская расскладка, то код будет выполниться, после try except ValueError.
            add_hotkey("shift + ё", lambda: asyncio.run(self.__exit_return_break("shift + ё")))
        # На других расскладках не проверялись.


        # Создание экземпляра класса Folder_make_list
        self.__fol_mak_lis = Folder_make_list(folder_list=self.__folder_list,
                                              neg_folder_list=self.__neg_folder_list,
                                              white_list=self.__white_list,
                                              black_list=self.__black_list,
                                              filter_work=self.__filter_work,
                                              append_white=self.__append_white)

        # Получение значений из экземпляра класса Folder_make_list
        self.__fomali_get_values()

        # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !
        # WARNING!!! Эти переменные нужны, для стабильности работы кода! Никогда не трогайте их! Сломаете стабильность кода.
        # Без этого списка, ищет все папки, абсолютно все папки.
        # Ни в коем случае, не ТРОГАЙТЕ эти переменные __ascii_upper, __RECYCLEBIN, __WINDOWS, __BLACK_NEGATIVE_LIST!!!
        # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !
        self.__ascii_upper = list(dict.fromkeys(ascii_letters.upper()))
        self.__RECYCLEBIN = [letter + ":\\$RECYCLE.BIN" for letter in self.__ascii_upper]
        self.__WINDOWS = [letter + ":\\Windows" for letter in self.__ascii_upper]
        self.__BLACK_NEGATIVE_LIST = self.__RECYCLEBIN + self.__WINDOWS
        # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !


    async def __exit_return_break(self,key): # __on_callback
        self.__ex_return = True
        # print('pressed', key)
        # await asyncio.sleep(1)
        # print('end for', key)


    # Функция folder_make_list принимает параметры, определяющие пути к папкам, фильтрам и другим настройкам
    def folder_make_list(self,
                         folder_list: Union[List[str], str] = None,
                         neg_folder_list: Optional[Union[List[str], str]] = None,
                         white_list: Optional[Union[List[str], str]] = None,
                         black_list: Optional[Union[List[str], str]] = None,
                         filter_work: Optional[Union[bool, str, int, float]] = False,
                         append_white: Optional[Union[bool, str, int, float]] = False):

        # Присваиваем значения атрибутам класса Folder_make_list
        # Обновляем свойства экземпляра класса Folder_make_list
        self.__fol_mak_lis.folder_list = folder_list
        self.__fol_mak_lis.neg_folder_list = neg_folder_list
        self.__fol_mak_lis.white_list = white_list
        self.__fol_mak_lis.black_list = black_list
        self.__fol_mak_lis.filter_work = filter_work
        self.__fol_mak_lis.append_white = append_white

        # Вызываем метод для обновления переменных класса
        # Получаем значения из экземпляра класса Folder_make_list
        self.__fomali_get_values()

        self.__fml = True
        # Обновляем список изображений
        self.get_image_list()
        self.__fml = False

    def __fomali_get_values(self):
        # Обновление переменных класса значениями из экземпляра класса Folder_make_list
        self.__folder_list = self.__fol_mak_lis.folder_list
        self.__neg_folder_list = self.__fol_mak_lis.neg_folder_list
        self.__white_list = self.__fol_mak_lis.white_list
        self.__black_list = self.__fol_mak_lis.black_list
        self.__filter_work = self.__fol_mak_lis.filter_work
        self.__append_white = self.__fol_mak_lis.append_white

    def find_image_list(self,
                        new_folder_list: Union[List[str], str] = None,
                        new_neg_folder_list: Optional[Union[List[str], str]] = None,
                        new_white_list: Optional[Union[List[str], str]] = None,
                        new_black_list: Optional[Union[List[str], str]] = None,
                        filter_work: Optional[Union[bool, str, int, float]] = None,
                        append_white: Optional[Union[bool, str, int, float]] = None,
                        save_every_n:int = None,
                        window_PySimpleGUI = None,
                        get_widget_PySimpleGUI = None,
                        update_PySimpleGUI = None):

        if not isinstance(save_every_n, NoneType):
            self.__save_every_n = save_every_n
        else:
            self.__save_every_n = 100

        new_folder_list = new_folder_list if new_folder_list != [""] else None
        new_neg_folder_list = new_neg_folder_list if new_neg_folder_list != [""] else None
        new_white_list = new_white_list if new_white_list != [""] else None
        new_black_list = new_black_list if new_black_list != [""] else None

        # Отключает ex_return, переключает в исходное положение.
        self.__ex_return = False

        print("Начинаем сбор изображений")
        print("Проверяем на наличие пустых папок")
        # Устанавливаем новые значения атрибутов, если они были переданы, иначе оставляем старые
        self.__new_folder_list = new_folder_list if new_folder_list != None else self.__folder_list
        self.__new_neg_folder_list = new_neg_folder_list if new_neg_folder_list != None else self.__neg_folder_list
        self.__new_white_list = new_white_list if new_white_list != None else self.__white_list
        self.__new_black_list = new_black_list if new_black_list != None else self.__black_list
        self.__new_filter_work = filter_work if filter_work != None else self.__filter_work
        self.__new_append_white = append_white if append_white != None else self.__append_white
        print("Обработано на наличие пустых папок")

        print(self.__new_folder_list)
        print(self.__new_neg_folder_list)
        print(self.__new_white_list)
        print(self.__new_black_list)
        print(self.__new_filter_work)
        print(self.__new_append_white)

        print("Вызываем метод поиска изображений с новыми параметрами")
        # Вызываем метод поиска изображений с новыми параметрами
        self.__fol_mak_lis.find(new_folder_list=self.__new_folder_list,
                                new_neg_folder_list=self.__new_neg_folder_list,
                                new_white_list=self.__new_white_list,
                                new_black_list=self.__new_black_list,
                                filter_work=self.__new_filter_work,
                                append_white=self.__new_append_white,
                                image_filenames=self.__image_filenames,
                                save_every_n=self.__save_every_n,
                                window_PySimpleGUI=window_PySimpleGUI,
                                get_widget_PySimpleGUI=get_widget_PySimpleGUI,
                                update_PySimpleGUI=update_PySimpleGUI)

        # С префиксом new_, они не сохраняются.
        print("Очищаем временные атрибуты")
        # Очищаем временные атрибуты
        self.__new_folder_list = None
        self.__new_neg_folder_list = None
        self.__new_white_list = None
        self.__new_black_list = None
        self.__new_filter_work = None
        self.__new_append_white = None

        self.__fml = True
        print("Обновляем список изображений")
        # Обновляем список изображений
        self.get_image_list()
        self.__fml = False

    def get_image_list(self):
        # Получаем список изображений из класса Folder_make_list
        if self.__fml:
            self.__image_filenames = self.__fol_mak_lis.image_list
        # Возвращаем список изображений
        return self.__image_filenames

    @property
    def image_list(self):
        # Возвращаем список изображений через свойство
        return self.__image_filenames

    @image_list.setter
    def image_list(self, img_lst: list):
        # Устанавливаем новый список изображений
        self.__image_filenames = img_lst

    @property
    def pickle_file(self):
        # Возвращаем список векторных представлений изображений через свойство
        try:
            return self.__all_image_features
        except AttributeError:
            return None

    @pickle_file.setter
    def pickle_file(self,
                    filename_pkl=PKL_FILE_PATH,
                    temp_pkl=TEMP_VAL):
        # Устанавливаем имена файлов для загрузки и временный файл
        self.__filename_pkl = filename_pkl
        self.__temp_pkl = temp_pkl
        # Загружаем векторные представления изображений
        self.__all_image_features = load_pkl(self.__filename_pkl, self.__temp_pkl)

    @property
    def model(self):
        # Возвращаем модель через свойство
        return self.__model

    @model.setter
    def model(self, in_model):
        # Присваиваем новую модель
        self.__model = in_model

    @property
    def preprocess(self):
        # Возвращаем препроцессор через свойство
        return self.__preprocess

    @preprocess.setter
    def preprocess(self, in_preprocess):
        # Присваиваем новый препроцессор
        self.__preprocess = in_preprocess

    @property
    def device(self):
        # Возвращаем девайс через свойство
        return self.__device

    @device.setter
    def device(self, in_device):
        # Устанавливаем новый девайс
        self.__device = in_device

    # Функция exists_in_image_folder проверяет, содержится ли изображение
    # с определенным идентификатором в списке имён изображений
    def exists_in_image_folder(self, image_id, image_filenames):
        # Проверяем, содержится ли изображение в списке
        if image_id in image_filenames:
            # Если да, возвращаем True
            return True
        # В противном случае, возвращаем False
        return False

    # Функция sync_clip_image_features синхронизирует векторные представления изображений с именами изображений
    def sync_clip_image_features(self, all_image_features, image_filenames):
        for_deletion = []
        # Перебираем векторные представления
        for i, aif in enumerate(all_image_features):
            # Печать номера текущего изображения
            # print(i)

            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break

            if not self.exists_in_image_folder(aif['image_id'], image_filenames):
                # Печать сообщения о удалении векторного представления
                print("deleting " + str(aif['image_id']))
                for_deletion.append(i)
        # Удаляем ненужные векторные представления
        for i in reversed(for_deletion):
            # Удаление векторного представления из списка
            del all_image_features[i]
        # Возвращаем обновленный список векторных представлений
        return all_image_features

    # Функция exists_in_all_image_features проверяет,
    # содержится ли изображение с определенным идентификатором
    # в списке всех векторных представлений изображений
    def exists_in_all_image_features(self, image_id, all_image_features):
        # Перебираем векторные представления
        for image in all_image_features:

            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break
            if image['image_id'] == image_id:
                # Если изображение найдено, возвращаем True
                # Показать сообщение, если изображение уже обработано
                # print("skipping "+ str(image_id))
                return True
        return False

    # Функция get_features извлекает векторные представления изображений с помощью модели CLIP
    # Предобработка изображения и подготовка его к использованию моделью
    def get_features(self, image):

        # Отключает ex_return, переключает в исходное положение.
        self.__ex_return = False

        try:
            # Предобработка изображения и подготовка его к использованию моделью
            # print("Предобработка изображения и подготовка его к использованию моделью")
            # print("1")
            image = self.__preprocess(image)
            # print("2")
            image = image.unsqueeze(0)
            # print("3")
            image = image.to(self.__device)

            # Выполнение операции без отслеживания градиентов
            # print("Выполнение операции без отслеживания градиентов")
            with torch.no_grad():
                # Извлечение векторного представления изображения
                image_features = self.__model.encode_image(image)
                # Нормализация векторов
                image_features /= image_features.norm(dim=-1, keepdim=True)
            # Возвращение numpy массива с векторами
            return image_features.cpu().numpy()
        except OSError as e:
            print(e)

    def create_clip_image_features(self,
                                   all_image_features = None,
                                   image_filenames: list = None,
                                   save_every_n: int = 100,
                                   check_image_paths: bool = True):
        # Отключает ex_return, переключает в исходное положение.
        self.__ex_return = False


        if not isinstance(all_image_features, NoneType) and check_image_paths:

            # Проверяем на существование путей изображений
            print("Проверяем на существование путей изображений")
            print(f"Колличество изображения до проверки: {len(all_image_features)}")
            for img in all_image_features:
                if not isfile(img.get("image_id")):
                    all_image_features.remove(img.get("image_id"))
                    print(f"Удаляется, так как он, не существует: {img.get('image_id')}")
                else:
                    try:
                        image = Image.open(img.get("image_id"))
                    except TypeError as e:
                        all_image_features.remove(img.get("image_id"))
                        print(e)
                        print(f"Удаляется, так как он, не является изображением: {img.get('image_id')}")

            print(f"Колличество изображения, после проверки: {len(all_image_features)}")

        if not isinstance(save_every_n,NoneType):
            self.__save_every_n = save_every_n

        # Загружаем все изображения из файла или из списка
        print("Загружаем все изображения из файла или из списка")
        try:
            self.__all_image_features = load_pkl(self.__filename_pkl, self.__temp_pkl)
        except Exception as e:
            self.__all_image_features = None
            print(f"Нет pkl файла:{e}")


        print("Если все_image_features не переданы, используем те, что уже есть")
        # Если все_image_features не переданы, используем те, что уже есть
        if isinstance(all_image_features, NoneType) and not isinstance(self.__all_image_features, NoneType):
            all_image_features = self.__all_image_features

        print("Если image_filenames не переданы, используем те, что уже есть")
        # Если image_filenames не переданы, используем те, что уже есть
        if isinstance(image_filenames, NoneType):
            image_filenames = self.__image_filenames

        print("Синхронизируем векторные представления изображений")
        # Вызов функции sync_clip_image_features для синхронизации векторных представлений
        # Синхронизируем векторные представления изображений
        all_image_features = self.sync_clip_image_features(all_image_features, image_filenames)

        print("Проходимся по списку изображений")
        # Проходимся по списку изображений
        for i, image_id in enumerate(tqdm(image_filenames)):
            # Выводим номер и имя изображения
            print(i, image_id)

            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break

            # Проверяем, существует ли изображение в уже обработанных
            if self.exists_in_all_image_features(image_id, all_image_features):
                # Если да, пропускаем
                continue

            # Попытка открыть изображение
            # print("Попытка открыть изображение")
            # print(image_id)
            try:
                image = Image.open(image_id)
                if image.mode != "RGBA":
                    image = image.convert('RGBA')
                # print("Получаем векторные представления изображения")
                # Получаем векторные представления изображения
                image_features = self.get_features(image)
                # print("Добавляем данные в список всех изображений")
                # Добавляем данные в список всех изображений
                all_image_features.append({'image_id': image_id, 'features': image_features})
            # Обработка исключения NameError
            except NameError as e:
                print("NameError:", e)
                continue
            # Обработка других исключений
            except Exception as e:
                print("Exception:", e)
                continue

            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break

            # Сохраняем результаты через определенные интервалы
            # Сохранять через каждые N шагов
            # save_every_n
            if i % self.__save_every_n == 0:
                # Сохраняем векторные представления изображений в файл pkl
                save_pkl(all_image_features, PKL_FILE_PATH)
                # Сохраняем список изображений в self.__all_image_features через каждые N шагов
                self.__all_image_features = all_image_features
                print(len(self.__all_image_features))
        # Сохраняем окончательные результаты
        save_pkl(all_image_features, PKL_FILE_PATH)
        # Сохраняем список изображений в self.__all_image_features
        self.__all_image_features = all_image_features

    @staticmethod
    def pil_to_numpy(img):
        """Конвертирует объект PIL Image в NumPy тензор."""
        img = img.convert('RGBA')
        img = np.asarray(img)
        return img

    @staticmethod
    def convert_image(input_data: Union[str, Image.Image], is_str: bool = False) -> Optional[Image.Image]:
        """
        Конвертирует данные в изображение.

        Принимаемые типы данных:
            - Строка: путь к файлу
            - Объект PIL.Image: непосредственно изображение

        Возвращаемый тип данных:
            - Объект PIL.Image
        """

        def pil_to_numpy(img):
            """Конвертирует объект PIL Image в NumPy тензор."""
            img = img.convert('RGBA')
            img = np.asarray(img)
            return img

        # Если input_data - строка, значит это путь к файлу
        if isinstance(input_data, str):
            # Если input_data - строка, значит это путь к файлу
            try:
                # Попытка открыть изображение
                image = Image.open(input_data)
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')

            except FileNotFoundError as e:
                # Если файл не найден, выводим сообщение и возвращаем None 
                # (если is_str = True, то вернуть True)
                print("Файл не найден:", e)
                return None if not is_str else True
            except PermissionError as e:
                print(e)
                return None
            else:
                # Если input_data - строка, значит это путь к файлу
                # и открытие прошло успешно, возвращаем объект PIL.Image
                # (если is_str = True, то вернуть False)
                return image if not is_str else False
            
        elif isinstance(input_data, Image.Image):
            if input_data.mode != "RGBA":
                input_data.convert("RGBA")
            # Если input_data - уже объект PIL.Image, просто вернуть его
            # (если is_str = True, то вернуть False)
            return input_data if not is_str else False
        else:
            # Если input_data - неверный тип данных, выбрасываем исключение
            print("Неизвестный тип данных")
            # raise ValueError("Неизвестный тип данных")
            return None

    def searcher_clip(self,
                      query_image_pillow: Union[str, Image.Image] = None,
                      query_str_pillow: Optional[Union[List[str], str]] = None,
                      image_filenames: dict = None,
                      image_features=None,
                      path_clip_image: str = None,
                      file_names=None,
                      file_names_path=None,
                      is_str: bool = False,
                      len_count: int = 10):
        """
        Метод для поиска ближайших соседей по изображению или тексту.

        Он принимает несколько параметров:
            - `query_image_pillow`: изображение, по которому будет выполняться поиск.
            - `query_str_pillow`: текст, по которому будет выполняться поиск.
            - `image_filenames`: список имeн файлов, которые будут использоваться для поиска.
            - `image_features`: список признаков изображений, которые будут использоваться для поиска.
            - `path_clip_image`: путь к файлу, в котором хранятся признаки изображений.
            - `file_names`: список имeн файлов, которые будут использоваться для поиска.
            - `file_names_path`: путь к папке, в которой хранятся файлы, которые будут использоваться для поиска.
            - `is_str`: флаг, указывающий, является ли `query_str_pillow` строкой или нет.

        Метод возвращает список найденных изображений.

        :param query_image_pillow: Query image, optional
        :type query_image_pillow: str or PIL.Image.Image
        :param query_str_pillow: Query string, optional
        :type query_str_pillow: str or List[str]
        :param image_filenames: List of image filenames, optional
        :type image_filenames: List[str]
        :param image_features: List of image features, optional
        :type image_features: List[np.ndarray]
        :param path_clip_image: Path to the file containing the image features, optional
        :type path_clip_image: str
        :param file_names: List of filenames, optional
        :type file_names: List[str]
        :param file_names_path: Path to the folder containing the files, optional
        :type file_names_path: str
        :param is_str: Flag indicating whether `query_str_pillow` is a string or not, optional
        :type is_str: bool
        :return: List of found images
        :rtype: List[PIL.Image.Image]

        query_image_pillow – это путь к изображению или само изображение Pillow для поиска.
        query_str_pillow – список строк или строка для поиска.
        image_filenames – словарь имён файлов изображений.
        image_features – массив характеристик изображений.
        path_clip_image – путь к файлу сохраненных характеристик.
        file_names – имена файлов для найденных результатов.
        file_names_path – пути к файлам для найденных результатов.
        is_str – флаг, определяющий, является ли поиск текстовым.
        len_count – количество результатов, которое нужно вернуть. По умолчанию 10.
        """


        # Отключает ex_return, переключает в исходное положение.
        self.__ex_return = False


        # Вложенные определения переменных
        # Эти переменные привязываются к экземпляру класса через __
        self.__query_image_pillow = query_image_pillow
        self.__query_str_pillow = query_str_pillow
        self.__image_filenames = image_filenames
        self.__image_features = image_features
        self.__path_clip_image = path_clip_image
        self.__file_names = file_names
        self.__file_names_path = file_names_path
        self.__is_str = is_str
        self.__len_count = len_count if len_count > 0 else 1
        
        ##########################
        # Настройка параметров   #
        ##########################

        # Обработка пустых значений
        # Если путь к клипу (path_clip_image) отсутствует,
        # используется предопределённый путь (PKL_FILE_PATH).
        # Если путь к клипу не определен, используется значение по умолчанию
        if isinstance(path_clip_image, NoneType):
            self.__path_clip_image = PKL_FILE_PATH

        # FIX: IndexError: list index out of range
        self.__file_names_path = file_names_path or self.__file_names_path or JSON_FILE_PATH
        self.__file_names = file_names or load_json_file(self.__file_names_path)
        print(f"file_names: {file_names}")
        print(f"file_names_path: {len(load_json_file(self.__file_names_path))}")
        # Загрузка данных из файла
        # Если характеристики изображений (image_features) отсутствуют,
        # они загружаются из файла (self.__path_clip_image).
        # Загрузка признаков изображений, если они еще не загружены
        print("Загрузка признаков изображений")
        if path.exists(self.__path_clip_image):
            print(f"Проверяем файл {self.__path_clip_image}")
            if isinstance(image_features, NoneType) and isinstance(self.__image_features, NoneType) or isinstance(self.__image_features, NoneType):
                print("Загружаю image_features")
                try:
                    self.__image_features = pk.load(open(self.__path_clip_image, "rb"))
                except EOFError:
                    print(f"Повреждён файл: {self.__path_clip_image}")
                    print("Возможно это случилось, когда вы нажали на поиск по тексту, \nи установлена галочка на автоудаление, и во время обучалась модель.")
                    return None
                except pk.UnpicklingError:
                    print(f"Данные pickle были усечены: {self.__path_clip_image}")
        else:
            print(f"Простите, не удаётся найти файл, {self.__path_clip_image}")
            print("Попробуйте нажать на кнопку | Начать обучать модель |")
            print("А после, попробуйте снова нажать на поиск текста, или изображение")
            return None

        ##########################
        # Преобразование признаков #
        ##########################

        # Подготовка характеристик для поиска
        # Характеристики изображений преобразуются в
        # NumPy массив и вычисляется их длина.
        self.__features = []
        # Преобразование характеристик изображений в NumPy массив
        for image in self.__image_features:
            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break

            # Векторная нормализация
            # Нормализация дает нам более точные результаты поиска
            self.__features.append(np.array(image['features']))
            # self.__features.append(np.asarray(image['features'], dtype="object")) #NOT FIX

        # Сохранение в NumPy массив
        # array - создает NumPy массив
        self.__features = np.array(self.__features)
        # self.__features = np.asarray(self.__features, dtype="object") #NOT FIX
        # squeeze - удаляет измерение из массива
        self.__features = np.squeeze(self.__features)
        #  выводит в консоль информацию о длине массива
        print(f"len features = {len(self.__features)}")

        ##########################
        # Подготовка поискового изображения #
        ##########################



        # Установка параметров поиска
        # Устанавливаются параметры индекса HNSW и
        # производится добавление элементов.
        if self.__is_str:
            # Создание папки для сохранения результатов
            isdir_makefolder(PATH_SEARCH_RES)
            # Колличество ближайших соседей
            self.__k = self.__len_count
            # Если колличество ближайших соседей больше количества признаков, то берём колличество признаков
            self.__k = self.__k if len(self.__features) >= self.__k else len(self.__features)
            print(f"k = {self.__k}")


            # Поиск ближайших соседей с помощью иерархического маленького мира
            # Определение размера вектора
            # Здесь определяется размер вектора (в данном случае 512).
            self.__dim = 512 # Размер вектора
                       # 512

            # Создание индекса HNSW с пространством L2 и заданной размерностью.
            # Также задаются параметры индексации,
            # включая максимальное количество элементов (max_elements),
            # значение параметра ef_construction и значение параметра M.
            self.__index = hnswlib.Index(space='l2', dim=self.__dim)
            self.__index.init_index(max_elements=len(self.__features), ef_construction=2500, M=32)
                                                #len(self.__features)# ef_construction=100, M=16
            # Добавление элементов в индекс
            self.__index.add_items(self.__features)

            # Печать максимального количества элементов:
            # Печатается текущее значение максимального количества элементов в индексе.
            print(f"{self.__index.max_elements = }")

            # Фиттинг модели ближайших соседей
            # Вызывается метод fit_NearestNeighbors,
            # который, вероятно, выполняет фиттинг модели ближайших соседей.
            # Параметры включают список имён файлов и пути к ним.
            self.fit_NearestNeighbors(self.__file_names, self.__file_names_path)

            # Показать длины списка файлов и пути к файлам.
            print(f"{len(self.__file_names) = }")
            print(f"{self.__file_names_path = }")

            # Преобразование текста
            # Текстовые запросы фильтруются и переводятся.
            # Фильтрация списка строк
            # Вызывается функция filter_str_list,
            # которая, вероятно, фильтрует список строк.
            self.__query_str_pillow = filter_str_list(self.__query_str_pillow)
            for i, text in enumerate(self.__query_str_pillow):

                if self.__ex_return:  # Остановка цикла, если ex_return == True
                    break

                # Каждый текст, переводит на английский язык.
                to_lang = "auto" # входящий язык, с которого переводим
                from_lang = "en" # выходящий язык, на который переводим
                # перевод текста в английский язык и сохранение в переменную temp_translation
                temp_translation = mini_translator(text, to_lang, from_lang)
                # перезапись в self.__query_str_pillow[i] переведенного текста
                self.__query_str_pillow[i] = temp_translation

            # Вычисление векторов текста
            # Выполняется поиск ближайших точек для каждого текстового запроса.
            for in_text in self.__query_str_pillow:

                if self.__ex_return:  # Остановка цикла, если ex_return == True
                    break

                # Токенизирует текст
                self.__text_tokenized = clip.tokenize(in_text).to(self.__device)
                with torch.no_grad():
                    # Кодирует текст
                    self.__text_features = self.__model.encode_text(self.__text_tokenized)
                    # Нормализует вектор
                    self.__text_features /= self.__text_features.norm(dim=-1, keepdim=True)
                
                # Устанавливает значение k
                self.__k = self.__len_count
                # Если k меньше или равно количеству изображений, то k = количество изображений, иначе k = k
                self.__k = self.__k if len(self.__file_names) >= self.__k else len(self.__file_names)
                print(f"{self.__k = }")
                # Печатает длину списка текстовых векторов
                print(f"{len(self.__text_features) = }")

                # Запрашиваем KNN для заданного текста и возвращаем его результаты.
                # self.__text_features.cpu().numpy() это текстовые векторы в виде numpy-массива.
                # self.__k это количество ближайших соседей, которое мы хотим получить.
                # self.__distances это список расстояний до ближайших соседей.
                self.__labels, self.__distances = self.__index.knn_query(self.__text_features.cpu().numpy(), k=self.__k)

                # Формирование результата
                # Сформированный результат отображает для найденных изображений.
                self.__images_np_hnsw_clip_text = []
                # Печатает длину списка self.__labels
                print(f"{self.__labels = }")
                # убираем список self.__labels[0]
                self.__labels = self.__labels[0]

                # Проходимся по списку изображений
                for i, idx in enumerate(self.__labels):

                    if self.__ex_return:  # Остановка цикла, если ex_return == True
                        break

                    # Печатает номер и имя изображения
                    # Если в self.__file_names[idx] нет значений None, то печатает имя файла
                    if self.__file_names is not None:
                        # Печатает имя файла
                        print(f'{self.__file_names[idx]}')

                    try:
                        # Печатает имя файла
                        print(f'{self.__file_names[idx]}')
                        # Открывает изображение
                        self.__img2 = Image.open(f'{self.__file_names[idx]}')

                        # Разделяет имя файла
                        self.__filename = ".".join(self.__file_names[idx].split("\\")[-1].split(".")[:-1])
                        # Разделяет расширение
                        self.__file_extension = "." + self.__file_names[idx].split("\\")[-1].split(".")[-1]
                        # Печатает имя и расширение
                        print(self.__filename, self.__file_extension)
                        # Создаёт директорию
                        print(f"До: {in_text}")
                        in_text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9-., ]',"", in_text)
                        print(f"После: {in_text}")

                        isdir_makefolder(PATH_SEARCH_RES + in_text)
                        # Сохраняет изображение
                        self.__img2.save(
                            f"{PATH_SEARCH_RES}{in_text}\\{i}_img_{self.__filename}{self.__file_extension}")
                        # Присоединяет изображение к списку
                        self.__images_np_hnsw_clip_text.append(np.array(self.__img2))
                    except Exception as e:
                        # Печатает ошибку
                        print(e)
                        # Печатает значения для отладки
                        print(f'{in_text = }\n{idx = }\n{i = }')
                        # Продолжает цикл, игнорируя ошибку
                        continue

        else:
            if os.path.isfile(self.__query_image_pillow):
                # Если входящие изображения не переданы, используем те, что уже есть
                self.__query_image_pillow = self.convert_image(self.__query_image_pillow)
                # Сохраняет векторное представление изображения
                self.__query_image_features = self.get_features(self.__query_image_pillow)

                ##########################
                # Поиск ближайших соседей #
                ##########################

                # Устанавливает значение k
                self.__k = self.__len_count
                # Если k меньше или равно количеству изображений, то k = количество изображений, иначе k = k
                self.__k = self.__k if len(self.__image_features) >= self.__k else len(self.__image_features)
                # Печатает значение k
                print(f"k = {self.__k}")
                print(f"len image features = {len(self.__image_features)}")

                # Инициализирует объект NearestNeighbors с алгоритмом поиска ближайших соседей и метрикой "по Евклиду".
                # self.__features это векторные представления изображений.
                self.__knn = NearestNeighbors(n_neighbors=self.__k, algorithm='brute', metric='euclidean')
                # Обучает объект NearestNeighbors на векторных представлениях изображений.
                try:
                    self.__knn.fit(self.__features)
                except InvalidParameterError:
                    print("Ошибка. Пустая модель, пустой список изображений.")
                    print("Не удалось найти в пустой модели, изображение")
                    return None
                # Ищет ближайшие соседей по векторным представлениям изображений.
                # self.__indices это список индексов ближайших соседей.
                # Возвращает список индексов ближайших соседей для каждого изображения.
                self.__indices = self.__knn.kneighbors(self.__query_image_features, return_distance=False)
                # Создает пустой список для хранения найденных изображений.
                self.__found_images = []

                ##########################
                # Печать результатов     #
                ##########################

                # Печатает результаты поиска ближайших соседей
                print("Печатает результаты поиска ближайших соседей")
                print(self.__indices)

                ##########################
                # Добавление найденных изображений #
                ##########################

                # Если путь к файлам не передан, используем те, что уже есть
                self.fit_NearestNeighbors(self.__file_names, self.__file_names_path)

                # Проходимся по списку индексов ближайших соседей
                for i, x in enumerate(self.__indices[0]):
                    if self.__ex_return:  # Остановка цикла, если ex_return == True
                        break

                    if search_in_list(self.__file_names[x],self.__BLACK_NEGATIVE_LIST):
                        continue

                # Исключение, изображения которые не существуют (например, изображение с таким путём не существует)
                # try:
                    print(f"len file_names:{len(self.__file_names)}, index x:{x}, i:{i}")

                    # FIX: IndexError: list index out of range
                    # Переменная, которая хранит путь к изображению
                    self.__in_path = self.__file_names[x]
                    print(self.__in_path)
                    # Открываеи изображение с указанным путём и сохраняем его в self.__img1
                    self.__img1 = Image.open(self.__in_path)

                    # Переменные, которые хранят название и расширение файла
                    # self.__filename - имя файла без расширения
                    self.__filename = ".".join(self.__in_path.split("\\")[-1].split(".")[:-1])
                    # self.__file_extension - расширение файла
                    self.__file_extension = "." + self.__in_path.split("\\")[-1].split(".")[-1]
                    # Выводим имя и расширение
                    print(self.__filename, self.__file_extension)

                    # Сохраняет изображение в папку images_find (переменная PATH_SEARCH_RES) (Если нет папки, то создает её)
                    # PATH_SEARCH_RES = fr"{Path.cwd()}\..\data\images_find\"
                    isdir_makefolder(PATH_SEARCH_RES)
                    # Сохраняет в папку images_find с именем число_изображения_имя_файла_расширение
                    self.__img1.save(f"{PATH_SEARCH_RES}{i}_img_{self.__filename}{self.__file_extension}")
                    # Добавляет изображение в список self.__found_images
                    self.__found_images.append(np.array(self.__img1))
                # except Exception as e:
                #     print(e)
                #     continue

    def fit_NearestNeighbors(self, file_names: Optional[List[str]] = None, file_names_path: Optional[str] = None) -> None:
        """
        Метод для настройки параметров поиска ближайших соседей.

        file_names - список путей к файлам, которые нужно добавить в image_list.
        file_names_path - путь к файлу, который будет использоваться для записи image_list.

        :param file_names: list of str, optional
        :param file_names_path: str, optional
        :return: None
        """

        # Отключает ex_return, переключает в исходное положение.
        self.__file_names_path = file_names_path or self.__file_names_path or JSON_FILE_PATH
        self.__file_names = file_names or load_json_file(self.__file_names_path)
    
    
    def run(self, save_every_n:int=100, clip_load=CLIP_LOAD, replace_clip_model=False):

        # Отключает ex_return, переключает в исходное положение.
        self.__ex_return = False


        print("run started")
        # Определяем устройство для выполнения операций
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        # Выводим информацию о выбранном устройстве
        print("device:", self.__device)
        # Проверяем, нужно ли заменить модель и предобработку
        if replace_clip_model or (self.__model == None and self.__preprocess == None):
            print("create model and preprocess")
            # Выводим сообщение о создании модели и предобработке
            print(f"create model and preprocess, load clip: {clip_load}")
            # Загружаем модель и предобработку
            self.__model, self.__preprocess = clip.load(clip_load)

        # Устанавливаем частоту сохранения результатов
        if not isinstance(save_every_n, NoneType):
            self.__save_every_n = save_every_n

        # Находим список изображений
        self.find_image_list()
        print(fr"Колличество изображений {len(self.get_image_list())}")
        print("find_image_list finished")
        save_json_file(self.get_image_list())

        print(f"Обработанно изображений: {len(self.__all_image_features)}")
        print(f"Найдено изображений: {len(self.__image_filenames)}")

        # Создаем векторные представления изображений
        self.create_clip_image_features(self.__all_image_features, self.__image_filenames, self.__save_every_n)
        print("create_clip_image_features finished")

# if __name__ == "__main__":
#     # gen_clip = Generate_clip_features()
#     #
#     # gen_clip.find_image_list(new_folder_list=["Здесь пути к изображениям"])
#     # gen_clip.run()
#     #
#     # print(gen_clip.image_list)
#     #
#     # gen_clip.searcher_clip(query_image_pillow="Здесь поиск по изображению")
#     #
#     # list_text = ["minecraft", "Цветок", "Mario", "pixel", "voxel", "пейзаж", "горы", "background sky white"]
#     # gen_clip.searcher_clip(query_str_pillow=list_text, is_str=True)
#
#     gen_clip = Generate_clip_features()
#     gen_clip.find_image_list(new_folder_list=[r"ImageAISearch\folder_path"])
#
#
#     gen_clip.run()
#     gen_clip.searcher_clip(len_count=5, query_image_pillow=r"images\i_mario.jpg")
#
#     list_text = ["minecraft",
#                  "Цветок",
#                  "Mario",
#                  "pixel",
#                  "voxel",
#                  "пейзаж",
#                  "горы",
#                  "красивый закат солнца",
#                  "красный город в закате"]
#
#     gen_clip.searcher_clip(len_count=5, query_str_pillow=list_text, is_str=True)


