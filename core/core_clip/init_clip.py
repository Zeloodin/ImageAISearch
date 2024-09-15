import os
import pathlib
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

from core.tools import load_json_file
from core.tools.bool_tools import filter_bool
from core.tools.folder_tools import Folder_make_list, isdir_makefolder, filter_str_list
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
                 clip_load: str = CLIP_LOAD):
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
        self.__device = None
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

        # Загрузка всех изображений из файла или списка
        self.__all_image_features = load_pkl(self.__filename_pkl, self.__temp_pkl)

        # Создание списка имен изображений
        self.__image_filenames = []

        # Инициализация других переменных класса
        self.__folder_list = folder_list
        self.__neg_folder_list = neg_folder_list
        self.__white_list = white_list
        self.__black_list = black_list
        self.__filter_work = filter_work
        self.__append_white = append_white

        # Создание экземпляра класса Folder_make_list
        self.__fol_mak_lis = Folder_make_list(folder_list=self.__folder_list,
                                              neg_folder_list=self.__neg_folder_list,
                                              white_list=self.__white_list,
                                              black_list=self.__black_list,
                                              filter_work=self.__filter_work,
                                              append_white=self.__append_white)

        # Получение значений из экземпляра класса Folder_make_list
        self.__fomali_get_values()

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
                        append_white: Optional[Union[bool, str, int, float]] = None):

        # Устанавливаем новые значения атрибутов, если они были переданы, иначе оставляем старые
        self.__new_folder_list = new_folder_list if new_folder_list != None else self.__folder_list
        self.__new_neg_folder_list = new_neg_folder_list if new_neg_folder_list != None else self.__neg_folder_list
        self.__new_white_list = new_white_list if new_white_list != None else self.__white_list
        self.__new_black_list = new_black_list if new_black_list != None else self.__black_list
        self.__new_filter_work = filter_work if filter_work != None else self.__filter_work
        self.__new_append_white = append_white if append_white != None else self.__append_white

        # Вызываем метод поиска изображений с новыми параметрами
        self.__fol_mak_lis.find(new_folder_list=self.__new_folder_list,
                                new_neg_folder_list=self.__new_neg_folder_list,
                                new_white_list=self.__new_white_list,
                                new_black_list=self.__new_black_list,
                                filter_work=self.__new_filter_work,
                                append_white=self.__new_append_white)

        # С префиксом new_, они не сохраняются.

        # Очищаем временные атрибуты
        self.__new_folder_list = None
        self.__new_neg_folder_list = None
        self.__new_white_list = None
        self.__new_black_list = None
        self.__new_filter_work = None
        self.__new_append_white = None

        self.__fml = True
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
        return self.__all_image_features

    @pickle_file.setter
    def pickle_file(self,
                    filename_pkl=PKL_FILE_PATH,
                    temp_pkl=TEMP_VAL):
        # Устанавливаем имена файлов для загрузки и временный файл
        self.__filename_pkl = filename_pkl
        self.__temp_pkl = temp_pkl
        # Загружаем векторные представления изображений
        self.__all_image_features = load_pkl(self.__filename_pkl, self.__temp_pkl)

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
            if image['image_id'] == image_id:
                # Если изображение найдено, возвращаем True
                # Показать сообщение, если изображение уже обработано
                # print("skipping "+ str(image_id))
                return True
        return False

    # Функция get_features извлекает векторные представления изображений с помощью модели CLIP
    # Предобработка изображения и подготовка его к использованию моделью
    def get_features(self, image):
        try:
            # Предобработка изображения и подготовка его к использованию моделью
            image = self.__preprocess(image).unsqueeze(0).to(self.__device)

            # Выполнение операции без отслеживания градиентов
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
                                   all_image_features=None,
                                   image_filenames: list = None):

        # Если все_image_features не переданы, используем те, что уже есть
        if isinstance(all_image_features, NoneType):
            all_image_features = self.__all_image_features

        # Если image_filenames не переданы, используем те, что уже есть
        if isinstance(image_filenames, NoneType):
            image_filenames = self.__image_filenames

        # Вызов функции sync_clip_image_features для синхронизации векторных представлений
        # Синхронизируем векторные представления изображений
        all_image_features = self.sync_clip_image_features(all_image_features, image_filenames)

        # Проходимся по списку изображений
        for i, image_id in enumerate(tqdm(image_filenames)):
            # Выводим номер и имя изображения
            print(i, image_id)
            # Проверяем, существует ли изображение в уже обработанных
            if self.exists_in_all_image_features(image_id, all_image_features):
                # Если да, пропускаем
                continue

            # Попытка открыть изображение
            try:
                image = Image.open(image_id)
                # Получаем векторные представления изображения
                image_features = self.get_features(image)
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

            # Сохраняем результаты через определенные интервалы
            # Сохранять через каждые N шагов
            # save_every_n
            if i % self.__save_every_n == 0:
                save_pkl(all_image_features, PKL_FILE_PATH)
                self.__all_image_features = all_image_features
                print(len(self.__all_image_features))
        # Сохраняем окончательные результаты
        save_pkl(all_image_features, PKL_FILE_PATH)
        self.__all_image_features = all_image_features

    # Простая функция, создания и сбора изображений в pkl файл.
    #
    def run(self, save_every_n=100, clip_load=CLIP_LOAD, replace_clip_model=False):
        # Определяем устройство для выполнения операций
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        # Выводим информацию о выбранном устройстве
        print(self.__device)
        # Проверяем, нужно ли заменить модель и предобработку
        if replace_clip_model or (self.__model == None and self.__preprocess == None):
            # Выводим сообщение о создании модели и предобработке
            print(f"create model and preprocess, load clip: {clip_load}")
            # Загружаем модель и предобработку
            self.__model, self.__preprocess = clip.load(clip_load)

        # Устанавливаем частоту сохранения результатов
        self.__save_every_n = save_every_n

        # Находим список изображений
        self.find_image_list()

        print(f"Обработанно изображений: {len(self.__all_image_features)}")
        print(f"Найдено изображений: {len(self.__image_filenames)}")

        # Создаем векторные представления изображений
        self.create_clip_image_features(self.__all_image_features, self.__image_filenames)

    @staticmethod
    def convert_image(input_data, is_str=False):
        """
        Конвертирует данные в изображение.

        Принимаемые типы данных:
            - Строка: путь к файлу
            - Объект PIL.Image: непосредственно изображение

        Возвращаемый тип данных:
            - Объект PIL.Image
        """
        if isinstance(input_data, str):
            # Если input_data - строка, значит это путь к файлу
            try:
                image = Image.open(input_data)
            except FileNotFoundError as e:
                print("Файл не найден:", e)
                return None if not is_str else True
            else:
                return image if not is_str else False
        elif isinstance(input_data, Image.Image):
            # Если input_data - уже объект PIL.Image, просто вернуть его
            return input_data if not is_str else False
        else:
            raise ValueError("Неизвестный тип данных")

    def searcher_clip(self,
                      query_image_pillow: Union[str, Image.Image] = None,
                      query_str_pillow: Optional[Union[List[str], str]] = None,
                      image_filenames: dict = None,
                      image_features=None,
                      path_clip_image: str = None,
                      file_names=None,
                      file_names_path=None,
                      is_str: bool = False):
        self.__query_image_pillow = query_image_pillow
        self.__query_str_pillow = query_str_pillow
        self.__image_filenames = image_filenames
        self.__image_features = image_features
        self.__path_clip_image = path_clip_image
        self.__file_names = file_names
        self.__file_names_path = file_names_path
        self.__is_str = is_str

        ##########################
        # Настройка параметров   #
        ##########################

        # Если путь к клипу не определен, используется значение по умолчанию
        if isinstance(path_clip_image, NoneType):
            self.__path_clip_image = PKL_FILE_PATH

        # Загрузка признаков изображений, если они еще не загружены
        if isinstance(image_features, NoneType):
            self.__image_features = pk.load(open(self.__path_clip_image, "rb"))

        ##########################
        # Преобразование признаков #
        ##########################

        self.__features = []
        for image in self.__image_features:
            self.__features.append(np.array(image['features']))
        self.__features = np.array(self.__features)
        self.__features = np.squeeze(self.__features)

        print(isinstance(image_features, NoneType),
              isinstance(path_clip_image, NoneType),
              self.__path_clip_image,
              self.__image_features,
              len(self.__features),
              self.__features)

        ##########################
        # Подготовка поискового изображения #
        ##########################



        if self.__is_str and not self.__query_str_pillow is None:
            isdir_makefolder(PATH_SEARCH_RES)

            self.__dim = 512
            self.__index = hnswlib.Index(space='l2', dim=self.__dim)
            self.__index.init_index(max_elements=len(self.__features), ef_construction=100, M=16)
            self.__index.add_items(self.__features)

            self.fit_NearestNeighbors(self.__file_names, self.__file_names_path)

            for in_text in filter_str_list(self.__query_str_pillow):
                self.__text_tokenized = clip.tokenize(in_text).to(self.__device)
                with torch.no_grad():
                    self.__text_features = self.__model.encode_text(self.__text_tokenized)
                    self.__text_features /= self.__text_features.norm(dim=-1, keepdim=True)

                self.__labels, self.__distances = self.__index.knn_query(self.__text_features.cpu().numpy(), k=1)

                self.__images_np_hnsw_clip_text = []
                self.__labels = self.__labels[0]

                print(f"{self.__labels = }")
                for i, idx in enumerate(self.__labels):
                    if self.__file_names is not None:
                        print(f'{self.__file_names[idx]}')

                    try:
                        print(f'{self.__file_names[idx]}')
                        self.__img2 = Image.open(f'{self.__file_names[idx]}')

                        self.__filename = ".".join(self.__file_names[idx].split("\\")[-1].split(".")[:-1])
                        self.__file_extension = "." + self.__file_names[idx].split("\\")[-1].split(".")[-1]
                        print(self.__filename, self.__file_extension)

                        isdir_makefolder(PATH_SEARCH_RES)
                        self.__img2.save(f"{PATH_SEARCH_RES}{in_text}\\{self.__filename}_img_{i}{self.__file_extension}")

                        self.__images_np_hnsw_clip_text.append(np.array(self.__img2))
                    except Exception as e:
                        print(e)
                        print(f'{in_text = }\n{idx = }\n{i = }')
                        continue

        else:
            self.__query_image_pillow = self.convert_image(self.__query_image_pillow)
            self.__query_image_features = self.get_features(self.__query_image_pillow)

            ##########################
            # Поиск ближайших соседей #
            ##########################

            self.__knn = NearestNeighbors(n_neighbors=len(self.__image_features), algorithm='brute', metric='euclidean')
            self.__knn.fit(self.__features)
            self.__indices = self.__knn.kneighbors(self.__query_image_features, return_distance=False)
            self.__found_images = []

            ##########################
            # Печать результатов     #
            ##########################

            print(self.__indices)

            ##########################
            # Добавление найденных изображений #
            ##########################

            self.fit_NearestNeighbors(self.__file_names, self.__file_names_path)

            for i, x in enumerate(self.__indices[0]):
                try:
                    self.__in_path = self.__file_names[x]
                    print(self.__in_path)
                    self.__img1 = Image.open(self.__in_path)

                    self.__filename = ".".join(self.__in_path.split("\\")[-1].split(".")[:-1])
                    self.__file_extension = "." + self.__in_path.split("\\")[-1].split(".")[-1]
                    print(self.__filename, self.__file_extension)

                    isdir_makefolder(PATH_SEARCH_RES)
                    self.__img1.save(f"{PATH_SEARCH_RES}{self.__filename}_img_{i}{self.__file_extension}")

                    self.__found_images.append(np.array(self.__img1))
                except Exception as e:
                    print(e)
                    continue

    def fit_NearestNeighbors(self, file_names=None, file_names_path=None):
        if isinstance(self.__file_names_path, NoneType) and isinstance(file_names_path, NoneType):
            self.__file_names_path = JSON_FILE_PATH
        elif isinstance(self.__file_names_path, NoneType) and not isinstance(file_names_path, NoneType):
            self.__file_names_path = file_names_path
        elif not isinstance(self.__file_names_path, NoneType) and not isinstance(file_names_path, NoneType):
            self.__file_names_path = file_names_path
        else:
            self.__file_names_path = JSON_FILE_PATH

        if isinstance(self.__file_names, NoneType) and isinstance(file_names, NoneType):
            self.__file_names = load_json_file(self.__file_names_path)
        elif isinstance(self.__file_names, NoneType) and not isinstance(file_names, NoneType):
            self.__file_names = file_names
        elif not isinstance(self.__file_names, NoneType) and not isinstance(file_names, NoneType):
            self.__file_names = file_names
        else:
            self.__file_names = load_json_file(self.__file_names_path)

if __name__ == "__main__":
    gen_clip = Generate_clip_features()

    gen_clip.find_image_list(new_folder_list=["Здесь пути к изображениям"])
    gen_clip.run()

    print(gen_clip.image_list)

    gen_clip.searcher_clip(query_image_pillow="Здесь поиск по изображению")

    list_text = ["minecraft", "Цветок", "Mario", "pixel", "voxel", "пейзаж", "горы", "background sky white"]
    gen_clip.searcher_clip(query_str_pillow=list_text, is_str=True)
