""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

import os
from pathlib import Path
from types import NoneType
from typing import List, Optional, Union

from keyboard import add_hotkey # В случае, когда надо отключить
import asyncio # Во время выполнения, асинхронно выполняет, рядом с другими задачами

from string import ascii_letters

from tqdm import tqdm

from core.tools.bool_tools import filter_bool
from core.tools.variables import IMG_SUP_EXTS


def isdir_makefolder(path_folder):
    """
    Функция `isdir_makefolder` принимает путь к папке и проверяет, существует ли она. Если нет, то создает папку.

    Аргументы:
    - path_folder (str): Путь к папке, которую нужно проверить и создать.
    """
    ascii_upper = list(dict.fromkeys(ascii_letters.upper()))
    # Создаем список заглавных букв ASCII для определения корневых дисков
    letter_directory = tuple([letter + ":\\" for letter in ascii_upper])
    # Создаем кортеж путей к корневым дискам
    temp_list = path_folder
    # Создаем временный список для хранения пути к папке
    tmp_first = False
    # Устанавливаем флаг, чтобы определить, нужно ли добавить текущую рабочую директорию к пути
    if not path_folder.startswith(letter_directory):
        temp_list = f'{Path.cwd()}\\{path_folder}'
        # Добавляем текущую рабочую директорию, если путь не начинается с корневого диска
        tmp_first = True
    # Устанавливаем флаг в True, если текущая рабочая директория была добавлена
    temp_list = temp_list.split("\\")
    # Разделяем путь на список подпутей
    min_len = len(str(Path.cwd()).split("\\"))+1 if tmp_first else len(temp_list[1:])
    # Определяем минимальную длину списка подпутей, чтобы избежать создания лишних папок
    for i in range(len(temp_list)+1)[min_len:]:
        res_path = "\\".join(temp_list[:i])
        # Формируем путь к папке, которую нужно проверить
        print(res_path)
        # Выводим путь к папке для отладки
        if not os.path.isdir(res_path):
            os.mkdir(res_path)
            # Создаем папку, если она не существует
            print(f"make dir: {res_path}")
            # Выводим сообщение о создании папки

def filter_str_list(value: Union[List[str], str] = None):
    """
    Функция для фильтрации строк в списке.

    value: Строка или список строк для фильтрации.
    """
    if isinstance(value, (str, list)):
        if isinstance(value, list):
            return value
        else:
            return value.split("\n")
    else:
        # print("Значение должно быть, list или str")
        return []

def search_in_list(finder: str, find_list: list):
    for item in find_list:
        # print(finder.find(item), finder, item)
        if finder.find(item) != -1 and find_list != [""]:
            return True
    return False

class Folder_path:
    def __set_name__(self, owner, name):
        self.name = "_"+name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if self.is_str_list(value):
            if isinstance(value, list):
                instance.__dict__[self.name] = value
            else:
                instance.__dict__[self.name] = value.split("\n")

        elif isinstance(value, NoneType):
            instance.__dict__[self.name] = []

        else:
            print("Значение должно быть, list or str")
            instance.__dict__[self.name] = []

    @staticmethod
    def is_str_list(item):
        return isinstance(item, (str, list))

class Folder_make_list:
    """
    Добавляет изображения из указанных папок в список изображений.

    Parameters:
    -----------
    folder_list : list
        Список путей к папкам, содержащим изображения, которые необходимо добавить в image_list.

    neg_folder_list : list
        Список путей к папкам, которые запрещают добавлять в image_list.

    white_list : list
        Список путей к папкам, разрешают добавлять изображения, минуя neg_folder_list, добавлять в image_list.

    black_list : list
        Список путей к папкам, которые запрещают добавлять в image_list, и запрещает добавлять white_list.
    """

    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !
    # WARNING!!! Эти переменные нужны, для стабильности работы кода! Никогда не трогайте их! Сломаете стабильность кода.
    # Без этого списка, ищет все папки, абсолютно все папки.
    # Ни в коем случае, не ТРОГАЙТЕ эти переменные __ascii_upper, __RECYCLEBIN, __WINDOWS, __BLACK_NEGATIVE_LIST!!!
    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !
    __ascii_upper = list(dict.fromkeys(ascii_letters.upper()))
    __RECYCLEBIN = [letter + ":\\$RECYCLE.BIN" for letter in __ascii_upper]
    __WINDOWS = [letter + ":\\Windows" for letter in __ascii_upper]
    __BLACK_NEGATIVE_LIST = __RECYCLEBIN + __WINDOWS
    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !


    _folder_list = Folder_path()
    _neg_folder_list = Folder_path()
    _white_list = Folder_path()
    _black_list = Folder_path()

    _new_folder_list = Folder_path()
    _new_neg_folder_list = Folder_path()
    _new_white_list = Folder_path()
    _new_black_list = Folder_path()

    def __init__(self,
                 folder_list: Union[List[str], str] = None,
                 neg_folder_list: Optional[Union[List[str], str]] = None,
                 white_list: Optional[Union[List[str], str]] = None,
                 black_list: Optional[Union[List[str], str]] = None,
                 filter_work: Optional[Union[bool, str, int, float]] = False,
                 append_white: Optional[Union[bool, str, int, float]] = False,
                 image_filenames: Optional[List[str]] = []):
        """
        Конструктор класса Folder_make_list.

        folder_list: Список путей к папкам, содержащим изображения.
        neg_folder_list: Список путей к папкам, которые запрещают добавлять изображения.
        white_list: Список путей к папкам, разрешающим добавлять изображения, минуя neg_folder_list.
        black_list: Список путей к папкам, которые запрещают добавлять изображения и запрещают добавлять white_list.
        """

        self._folder_list = folder_list # Список путей, папок, изображений.
        self._neg_folder_list = neg_folder_list # Негативный список путей, который фильтрует folder_list.
        self._white_list = white_list # Белый список путей, который разрешает в запрещённом neg_folder_list.
        self._black_list = black_list # Чёрный список путей, который фильтрует все списки.
        self._image_list = [] # Список путей изображений.

        self._image_list = list(dict.fromkeys(list(self._image_list) + image_filenames))
        # print(len(self._image_list))

        self._filter_work = filter_bool(filter_work)
        self._append_white = filter_bool(append_white)

        # if not isinstance(image_filenames, NoneType) and self._image_list != image_filenames:
        #     for string in tqdm(image_filenames):
        #         if string not in self._image_list:
        #             self._image_list.append(string)

        # Код прерывает цикл, в _from_folder И _for_folder И negative_filter
        self.__ex_return = False
        try:
            # Если Английская расскладка, то код будет выполниться правильно.
            add_hotkey("shift + `", lambda: asyncio.run(self.__exit_return_break("shift + `")))
        except ValueError:
            # Если Русская расскладка, то код будет выполниться, после try except ValueError.
            add_hotkey("shift + ё", lambda: asyncio.run(self.__exit_return_break("shift + ё")))
        # На других расскладках не проверялись.

    @property
    def image_list(self):
        return self._image_list

    @property
    def folder_list(self):
        return self._folder_list
    @folder_list.setter
    def folder_list(self, new_value : Union[List[str], str]):
        # Применяется filter_str_list
        self._folder_list = filter_str_list(new_value)

    @property
    def neg_folder_list(self):
        return self._neg_folder_list
    @neg_folder_list.setter
    def neg_folder_list(self, new_value : Union[List[str], str]):
        # Применяется filter_str_list
        self._neg_folder_list = filter_str_list(new_value)

    @property
    def white_list(self):
        return self._white_list
    @white_list.setter
    def white_list(self, new_value: Union[List[str], str]):
        # Применяется filter_str_list
        self._white_list = filter_str_list(new_value)

    @property
    def black_list(self):
        return self._black_list
    @black_list.setter
    def black_list(self, new_value: Union[List[str], str]):
        # Применяется filter_str_list
        self._black_list = filter_str_list(new_value)

    @property
    def filter_work(self):
        return self._filter_work
    @filter_work.setter
    def filter_work(self, new_value: Union[bool, str, int, float] = False):
        # Применяется filter_bool
        self._filter_work = bool(filter_bool(new_value))

    @property
    def append_white(self):
        return self._append_white
    @append_white.setter
    def append_white(self, new_value: Union[bool, str, int, float] = False):
        # Применяется filter_bool
        self._append_white = bool(filter_bool(new_value))


    async def __exit_return_break(self,key): # __on_callback
        self.__ex_return = True
        # print('pressed', key)
        # await asyncio.sleep(1)
        # print('end for', key)

    @staticmethod
    def _is_str_list(item):
        """
        Проверяет, является ли элемент строкой или списком строк.

        Item: Элемент для проверки.
        """
        return isinstance(item, (str, list))

    def find(self,
             new_folder_list: Union[List[str], str] = None,
             new_neg_folder_list: Optional[Union[List[str], str]] = None,
             new_white_list: Optional[Union[List[str], str]] = None,
             new_black_list: Optional[Union[List[str], str]] = None,
             filter_work: Optional[Union[bool, str, int, float]] = False, # filter_while_working - Фильтровать во время работы
             append_white: Optional[Union[bool, str, int, float]] = False,
             image_filenames: Optional[List[str]] = None):

        """
        Добавляет изображения из указанных папок в список изображений.

        new_folder_list: Список путей к папкам, содержащим изображения, которые необходимо добавить в image_list.
        new_neg_folder_list: Список путей к папкам, которые запрещают добавлять в image_list.
        new_white_list: Список путей к папкам, разрешающим добавлять изображения, минуя neg_folder_list, добавлять в image_list.
        new_black_list: Список путей к папкам, которые запрещают добавлять в image_list, и запрещает добавлять white_list.
        filter_work: Флаг, указывающий, нужно ли фильтровать файлы во время поиска.
        append_white: Флаг, указывающий на необходимость добавления white_list в new_folder_list.

        Чем выше уровень, тем приоритетнее список над списками ниже уровня.
        1    new_folder_list
        2        new_neg_folder_list
        3            new_white_list
        4                new_black_list
        """

        # if not isinstance(image_filenames, NoneType) and self._image_list != image_filenames:
        #     for string in tqdm(image_filenames):
        #         if string not in self._image_list:
        #             self._image_list.append(string)

        print("Подготавливаем список")
        print(f"Колличество элементов в списке: {len(self._image_list)}")
        self._image_list = list(dict.fromkeys(list(self._image_list) + image_filenames))
        print(f"Колличество элементов в списке: {len(self._image_list)}")

        # print(len(self._image_list))

        # Отключает ex_return, переключает в исходное положение.
        self.__ex_return = False

        # Применяем фильтрацию строк в списках
        _new_folder_list = filter_str_list(new_folder_list)
        _new_neg_folder_list = filter_str_list(new_neg_folder_list)
        _new_white_list = filter_str_list(new_white_list)
        _new_black_list = filter_str_list(new_black_list)

        self._filter_work = filter_bool(filter_work)
        self._append_white = filter_bool(append_white)

        # Проверяем пустые списки и заменяем их на соответствующие значения из self
        self.is_list_empty(new_folder_list,
                           new_neg_folder_list,
                           new_white_list,
                           new_black_list)

        if append_white:
            self._new_folder_list += self._new_white_list

        # self.from_folder ищет по списку к путь изображению, через фильтрацию.
        print("Ищем по списку к путям ищображениям")
        self._from_folder(self._new_folder_list,
                         self._new_neg_folder_list,
                         self._new_white_list,
                         self._new_black_list,
                         filter_work = self._filter_work)
        print("Собрали изображения в список")

        if not self._filter_work:
            print("Переходим в фильтрацию, во время работы")
            # Если filter_work = True, проверяется во время поиска.
            # И не проверяется в negative_filter, так как, это лишняя проверка на уже пройденную фильтрацию.
            # self.negative_filter не работает, когда filter_work = True
            self._negative_filter(self._new_neg_folder_list,
                                 self._new_white_list,
                                 self._new_black_list)


    def _from_folder(self, new_folder_list=None,
                    new_neg_folder_list=None,
                    new_white_list=None,
                    new_black_list=None,
                    filter_work:bool = False):
        """
        Функция для поиска изображений в папках.

        new_folder_list: Список путей к папкам, содержащим изображения, которые необходимо добавить в image_list.
        new_neg_folder_list: Список путей к папкам, которые запрещают добавлять в image_list.
        new_white_list: Список путей к папкам, разрешающим добавлять изображения, минуя neg_folder_list, добавлять в image_list.
        new_black_list: Список путей к папкам, которые запрещают добавлять в image_list, и запрещает добавлять white_list.
        """

        # Проверяем пустые списки и заменяем их на соответствующие значения из self
        self.is_list_empty(new_folder_list,
                           new_neg_folder_list,
                           new_white_list,
                           new_black_list)

        print("Ищем в папках изображения")
        self._for_folder(filter_work)

    # Основная функция программы
    def _for_folder(self,_filter_work):
        # Проходим по всем папкам в списке
        for folder in self._new_folder_list:
            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break
            # Проходим по всем каталогам и подкаталогам в папке
            for root, dirs, files in os.walk(folder):
                if self.__ex_return:  # Остановка цикла, если ex_return == True
                    break
                # Вызываем функцию фильтрации файлов для каждого каталога
                self._filter_files(root, files, self._filter_work)

    # Функция для фильтрации файлов изображений в каталоге
    def _filter_files(self,root, files, _filter_work):
        """
        Эта функция фильтрует файлы изображений в указанном каталоге.

        Root (str): Путь к каталогу.
        Files (list): Список файлов в каталоге.
        Filter_work (bool): Флаг, указывающий, нужно ли фильтровать файлы.

        Возвращает:
        None: Ничего не возвращает, но изменяет список файлов.
        """

        for file in tqdm(files):
            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break
            # Проверяем, является ли файл изображением
            if file.lower().endswith(IMG_SUP_EXTS): #('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
                if self.__ex_return:  # Остановка цикла, если ex_return == True
                    break
                # Проверяем, есть ли файл в списке уже обработанных изображений

                if os.path.join(root, file) not in self._image_list and not self.__ex_return:
                    # Если нужно фильтровать файлы или фильтр возвращает True для файла, добавляем файл в список
                    if not self._filter_work or self._filter_string(os.path.join(root, file)):
                        # Добавляем файл в список изображений
                        self._image_list.append(os.path.join(root, file))
                        # print("Append", root, file)
                    else:
                        # Удаляем файл из списка изображений
                        # print("Remove", root, file)
                        continue

    def _negative_filter(self, new_neg_folder_list=None,
                        new_white_list=None,
                        new_black_list=None):

        # Проверяем пустые списки и заменяем их на соответствующие значения из self
        self.is_list_empty(new_neg_folder_list=new_neg_folder_list,
                           new_white_list=new_white_list,
                           new_black_list=new_black_list)

        print("Начинаем фильтровать список от негативного списка")
        print(f"Всего изображений: {len(self._image_list)}")

        # for i,img_lst in enumerate(tqdm(self._image_list)):
        for i in range(len(self._image_list)-1,-1,-1):
            img_lst = self._image_list[i]

            # print(f"{i} Всего изображений: {len(self._image_list)}")

            if self.__ex_return:  # Остановка цикла, если ex_return == True
                break
            if not self._filter_string(img_lst):
                self._image_list.remove(img_lst)
                # print("Remove", img_lst)

        print(f"Всего профильтрованных изображений: {len(self._image_list)}")

    def _filter_string(self,img_lst):
        # _new_neg_folder_list == False,
        # _new_white_list == True,
        # _new_black_list == False,
        # __BLACK_NEGATIVE_LIST == False
        #
        # True == positive White if not negative Black is False.
        # Возращает True, если списки пусты, и или разрешает _new_white_list, возращает True.
        # Возращает True, если есть в _new_neg_folder_list запрещает, но разрешает _new_white_list.
        # Возращает False, если в списке _new_white_list, есть в _new_black_list, то False.
        # Возращает False, если в списке new_folder_list, есть в _new_neg_folder_list, то False.
        #
        # F = new_folder_list
        # N = _new_neg_folder_list
        # W = _new_white_list
        # B = _new_black_list
        #  - - - - - - - - - - - - - - - - - - - - - - - - -
        # example 1
        # return (-N or W) and -B and -BN             IF
        # return (0 or 0) and 0 and 0                 INPUT
        # return (True or False) and True and True    RESULT
        # return True
        # - - - - - - - - - - - - - - - - - - - - - - - - -
        # example 2
        # return (-N or W) and -B and -BN             IF
        # return (0 or 1) and 0 and 0                 INPUT
        # return (True or True) and True and True     RESULT
        # return True
        # - - - - - - - - - - - - - - - - - - - - - - - - -
        # example 3
        # return (-N or W) and -B and -BN             IF
        # return (1 or 0) and 0 and 0                 INPUT
        # return (False or False) and True and True   RESULT
        # return False
        # - - - - - - - - - - - - - - - - - - - - - - - - -
        # example 4
        # return (-N or W) and -B and -BN             IF
        # return (0 or 0) and 1 and 0                 INPUT
        # return (True or False) and False and True   RESULT
        # return False
        # - - - - - - - - - - - - - - - - - - - - - - - - -

        N = search_in_list(img_lst, self._new_neg_folder_list)
        W = search_in_list(img_lst, self._new_white_list)
        B = search_in_list(img_lst, self._new_black_list)
        BN = search_in_list(img_lst, self.__BLACK_NEGATIVE_LIST)

        result = (not N or W) and not B and not BN
        return result

    def is_list_empty(self, new_folder_list = None,
                      new_neg_folder_list = None,
                      new_white_list = None,
                      new_black_list = None):
        # Проверяет пустые списки.
        # И если list пуст, то заменяется self.list.
        # А пустой list, удаляется. list = None.

        self._new_folder_list = new_folder_list \
            if new_folder_list and \
               len(new_folder_list) else self._folder_list

        self._new_neg_folder_list = new_neg_folder_list \
            if new_neg_folder_list and \
               len(new_neg_folder_list) else self._neg_folder_list

        self._new_white_list = new_white_list \
            if new_white_list and \
               len(new_white_list) else self._white_list

        self._new_black_list = new_black_list \
            if new_black_list and \
               len(new_black_list) else self._black_list

        # Не до конца разобрался с этми переменными, но они уже не нужны.
        # В любом случае надо освобождать, память не резиновая.
        del new_neg_folder_list
        del new_folder_list
        del new_white_list
        del new_black_list


# if __name__ == "__main__":
#     from core.tools.json_tools import save_json_file
#
#
#     folder_path_list = Folder_make_list(folder_list = [r"ImageAISearch"],
#                                         neg_folder_list = [r"ImageAISearch\venv",
#                                                            r"ImageAISearch\folder_path",
#                                                            r"ImageAISearch\images"],
#                                         white_list = [r"ImageAISearch\folder_path\sky.png",
#                                                       r"ImageAISearch\images\1526.jpg"])
#
#     folder_path_list.find(filter_work=True,
#                           append_white=True)
#     folder_path_list.find(new_white_list= r"..\\..\\project_folders")
#
#
#
#     print(folder_path_list.image_list)
#
#
#
#
#     save_json_file(folder_path_list.image_list,indent=0)