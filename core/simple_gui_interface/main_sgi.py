import os
import shutil
from pathlib import Path
import PySimpleGUI as sg
import torch
from clip import clip
import re
import asyncio
from types import NoneType

# Не получается ассихронизировать
# Во время выполнения, где собираются, обрабатываются данные,
# Программа застывает. И после выполнения, програма возобновляется снова.
# Чтобы программа работала ассихронно, нужно изучать как работает эта ассихроннизация.
# import asyncio

from core.core_clip.init_clip import Generate_clip_features
from core.tools import isfloat, isdir_makefolder
from core.tools.bool_tools import filter_bool
from core.tools.json_tools import save_json_file, load_json_file
from core.core_clip.save_clip import save_pkl
from core.core_clip.load_clip import load_pkl
from core.tools.variables import (
    IMG_EXTS,
    IMG_SUP_EXTS,
    IMG_FILE_TYPES,
    JSON_FILE_PATH,
    PKL_FILE_PATH,
    JSON_FILE_TYPES,
    PKL_FILE_TYPES,
    PATH_SEARCH_RES,
    CLIP_LOAD
)

from core.simple_gui_interface.gui_file_browser import popup_paths
from core.simple_gui_interface.commands import open_folder_in_explorer

# Создание класса Main_gui_image_search
class Main_gui_image_search:
    sg.theme('Dark Amber')


    def __init__(self) -> None:
        self.__right_click_menu = ['&Right', ['Вырезать', 'Копировать', 'Вставить', 'Удалить', 'Выделить всё']]

        self.__IN_JSON_PATH = JSON_FILE_PATH
        self.__IN_PKL_PATH = PKL_FILE_PATH

        self.__gen_clip = Generate_clip_features()



        try:
            self.__gen_clip.image_list = load_json_file(self.__IN_JSON_PATH)
        except Exception as e:
            pass
            # self.__gen_clip.image_list = []

        try:
            self.__gen_clip.pickle_file = load_pkl(self.__IN_PKL_PATH)
        except Exception as e:
            pass
            # self.__gen_clip.pickle_file = {}

        self._layout_main = [
            [[sg.Push(), self._build_json_frame(),
             self._build_pickle_frame()],
             sg.Frame("",[[self._build_basic_launch_parameters_frame()],
                        [sg.Push(), self._build_search_frame()]]),
             self._build_folder_multiline_list_frame()]]

        self._window = sg.Window(
            title="ImageAISearch",
            layout=self._layout_main,
            finalize=True,
            margins=(10, 10),
            font=(None,12),
            size=(1250, 700))

        # Раньше это работало отлично.
        # Сейчас, это перестало работать
        # При других символах, будет вызываться ошибка.
        # Надо в таких случаях, или выдавать ошибку в консоль, или заменять всё на ничего, кроме чисел.
        # Внимание, Сохранять каждые 0 шагов, вызовет ошибку. Это надо запомнить.
        self._vcmd = (self._window.TKroot.register(self.__validate_integer), '%P')
        self._window['-RESULT_QUANTITY_IMAGES_OUT-'].widget.configure(validate='all', validatecommand=self._vcmd)
        self._vcmd2 = (self._window.TKroot.register(self.__validate_integer), '%P')
        self._window['-SAVE_EVERY_N_JSON-'].widget.configure(validate='all', validatecommand=self._vcmd2)

        if self.__gen_clip.image_list:
            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
        else:
            if self.__gen_clip.pickle_file:
                self.__gen_clip.image_list = [n.get("image_id") for n in self.__gen_clip.pickle_file]
                self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
                save_json_file(self.__gen_clip.image_list, self.__IN_JSON_PATH)

        if self.__gen_clip.pickle_file:
            self._window["-TEXT_RESULT_COUNT_IMAGES-"].update(f"Всего обработанно изображений: {len(self.__gen_clip.pickle_file)}")

        self._window['-CHBX_CHECK_MODEL-'].set_focus()
        self._window['-CHBX_REPLACE_MODEL-'].set_focus()
        self._window['-BTN_CLIP_TRAIN-'].set_focus()
        self._window['-CHBX_FILTER_WORK_LIST-'].set_focus()
        self._window['-CHBX_APPEND_WHITE_LIST-'].set_focus()
        self._window['-TEXT_COUNT_IMAGES-'].set_focus()
        self._window['-TEXT_RESULT_COUNT_IMAGES-'].set_focus()
        self._window['-CHBX_SAVE_IMAGE_LIST-'].set_focus()
        self._window['-BTN_FOLDER_MAKE_LIST-'].set_focus()
        self._window['-BTN_POSITIVE_PATH_LIST-'].set_focus()
        self._window['-BTN_NEGATIVE_PATH_LIST-'].set_focus()
        self._window['-MULTI_POSITIVE_PATH_LIST-'].set_focus()
        self._window['-IN_TEXT_PATH-'].set_focus()
        self._window['-BTN_SEARCH_TEXT-'].set_focus()
        self._window['-BTN_SEARCH_PATH-'].set_focus()
        self._window['-FIBR_SEARCH_PATH-'].set_focus()
        self._window['-CHBX_CLEANUP_FIND_RES-'].set_focus()

        # # --------------------------------------------------------------
        # # добавляет к объектам фокус, чтобы не было проблем с действующими объектами.
        # # без .set_focus(), не корректно работает. Лучше их не трогать.
        # # --------------------------------------------------------------
        # # _build_search_frame
        self._window['-IN_TEXT_PATH-'].set_focus()
        self._window['-BTN_SEARCH_TEXT-'].set_focus()
        self._window['-BTN_SEARCH_PATH-'].set_focus()
        self._window['-FIBR_SEARCH_PATH-'].set_focus()
        # # --------------------------------------------------------------
        # # _build_json_frame
        # self._window['-IN_JSON_PATH-'].set_focus()
        # self._window['-BTN_JSON_SAVE_PATH-'].set_focus()
        # self._window['-FIBR_JSON_SAVE_PATH-'].set_focus()
        # self._window['-BTN_JSON_LOAD_PATH-'].set_focus()
        # self._window['-FIBR_JSON_LOAD_PATH-'].set_focus()
        # # --------------------------------------------------------------
        # # _build_pickle_frame
        # self._window['-IN_PKL_PATH-'].set_focus()
        # self._window['-BTN_PKL_SAVE_PATH-'].set_focus()
        # self._window['-FIBR_PKL_SAVE_PATH-'].set_focus()
        # self._window['-BTN_PKL_LOAD_PATH-'].set_focus()
        # self._window['-FIBR_PKL_LOAD_PATH-'].set_focus()
        # # --------------------------------------------------------------
        # # _build_folder_multiline_list_frame
        # self._window['-MULTI_POSITIVE_PATH_LIST-'].set_focus()
        # self._window['-MULTI_NEGATIVE_PATH_LIST-'].set_focus()
        # self._window['-MULTI_WHITE_PATH_LIST-'].set_focus()
        # self._window['-MULTI_BLACK_PATH_LIST-'].set_focus()
        #
        # self._window['-BTN_POSITIVE_PATH_LIST-'].set_focus()
        # self._window['-BTN_NEGATIVE_PATH_LIST-'].set_focus()
        # self._window['-BTN_WHITE_PATH_LIST-'].set_focus()
        # self._window['-BTN_BLACK_PATH_LIST-'].set_focus()
        # # --------------------------------------------------------------
        # # _build_make_folder_list_frame
        self._window['-BTN_FOLDER_MAKE_LIST-'].set_focus()
        self._window['-CHBX_SAVE_IMAGE_LIST-'].set_focus()
        self._window['-CHBX_APPEND_WHITE_LIST-'].set_focus()
        self._window['-CHBX_FILTER_WORK_LIST-'].set_focus()
        # # --------------------------------------------------------------
        # # _build_clip_tools_frame
        self._window['-CHBX_REPLACE_MODEL-'].set_focus()
        self._window['-RESULT_QUANTITY_IMAGES_OUT-'].set_focus()
        self._window['-RESULT_SHOW_IMAGES-'].set_focus()
        # # --------------------------------------------------------------



        print("run started")
        # Определяем устройство для выполнения операций
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        self.__gen_clip.device = self.__device
        # Выводим информацию о выбранном устройстве
        print("device:", self.__device)

        self.__replace_model = filter_bool(self._window['-CHBX_REPLACE_MODEL-'].get())

        # Проверяем, нужно ли заменить модель и предобработку
        if self.__replace_model or (self.__gen_clip.model == None or self.__gen_clip.preprocess == None):
            print("Создаём модель и препроцессор")
            # Выводим сообщение о создании модели и препроцессоре
            print(f"Создаём модель и препроцессор, загружаем clip: {CLIP_LOAD}")
            # Загружаем модель и предобработку
            self.__model, self.__preprocess = clip.load(CLIP_LOAD)

            self.__gen_clip.preprocess = self.__preprocess
            self.__gen_clip.model = self.__model







    def _build_search_frame(self):
        layout_search = [
            [sg.T("Введите текст, или путь к изображению, в каталоге файлов")],
            [sg.I(key="-IN_TEXT_PATH-", right_click_menu=self.__right_click_menu, font=(None,18), size=700)],
            [sg.Push(), sg.Frame("Текст",
                      [[sg.B(key="-BTN_SEARCH_TEXT-", button_text="Поиск по описанию")]]),

            sg.Frame("Изображение",
                     [[sg.B(key="-BTN_SEARCH_PATH-", button_text="Поиск по картинке"),

                     sg.I(key="-FIBR_SEARCH_PATH-", visible=False, size=(0, 0), disabled=True, enable_events=True),
                     sg.FileBrowse(#key="-FIBR_SEARCH_PATH-",
                                      button_text="Выбрать картинку",
                                      # enable_events=True,
                                      file_types=IMG_FILE_TYPES
                                   )]]), sg.Push()],

            [sg.Push(), sg.Frame("",[
            [sg.T(text="Показать"),
            sg.I(key="-RESULT_QUANTITY_IMAGES_OUT-", default_text=10, size=(10, 0)),
             sg.T(text="найденных изображений")],
            [sg.B(key="-RESULT_SHOW_IMAGES-", button_text="Показать результат")]
            ]), sg.Push()],
            [self._build_cleanup_images_find_frame()]
        ]
        return sg.Frame("Поисковой запрос", layout_search, size=(700,300))

    def _build_json_frame(self):
        layout_json = [
            [sg.T("Сохранить список путей изображений (json)")],
            [sg.I(key="-IN_JSON_PATH-",
                  default_text=self.__IN_JSON_PATH,
                  right_click_menu=self.__right_click_menu)],

            [sg.Frame("Кнопки сохранения",
            [[sg.B(key="-BTN_JSON_SAVE_PATH-", button_text="Сохранить список")],
            [sg.FileSaveAs(key="-FIBR_JSON_SAVE_PATH-",
                           button_text="Сохранить список как...",
                           enable_events=True,
                           file_types=JSON_FILE_TYPES)]]),

            sg.Frame("Кнопки загрузки",
            [[sg.B(key="-BTN_JSON_LOAD_PATH-", button_text="Загрузить список")],
            [sg.FileBrowse(key="-FIBR_JSON_LOAD_PATH-",
                           button_text="Загрузить список как...",
                           enable_events=True,
                           file_types=JSON_FILE_TYPES)]])]
        ]
        return sg.Frame("Загрузка и Сохранения списка изображений", layout_json, visible=False)

    def _build_pickle_frame(self):
        layout_pickle = [
            [sg.T("Сохранить базу данных изображений (pkl)")],
            [sg.I(key="-IN_PKL_PATH-",
                  default_text=self.__IN_PKL_PATH,
                  right_click_menu=self.__right_click_menu)],

            [sg.Frame("Кнопки сохранения",
            [[sg.B(key="-BTN_PKL_SAVE_PATH-", button_text="Сохранить базу данных")],
            [sg.FileSaveAs(key="-FIBR_PKL_SAVE_PATH-",
                           button_text="Сохранить базу данных как...",
                           enable_events=True,
                           file_types=PKL_FILE_TYPES)]]),

            sg.Frame("Кнопки загрузки",
            [[sg.B(key="-BTN_PKL_LOAD_PATH-", button_text="Загрузить базу данных")],
            [sg.FileBrowse(key="-FIBR_PKL_LOAD_PATH-",
                           button_text="Загрузить базу данных как...",
                           enable_events=True,
                           file_types=PKL_FILE_TYPES)]])]
        ]
        return sg.Frame("Загрузка и Сохранения база обработанных изображений", layout_pickle, visible=False)



    def _build_folder_multiline_list_frame(self):
        layout_folder_multiline_list = [
        [sg.Frame("Список папок изображений",[
            [sg.B("Выбрать файлы и папки",
                  key="-BTN_POSITIVE_PATH_LIST-")],
            [sg.Multiline(key="-MULTI_POSITIVE_PATH_LIST-",
                          size=(30, 12),
                          right_click_menu=self.__right_click_menu,
                          horizontal_scroll=True)
            ]]),

        sg.Frame("Белый список папок",[
            [sg.B("Выбрать файлы и папки",
                  key="-BTN_WHITE_PATH_LIST-")],
            [sg.Multiline(key="-MULTI_WHITE_PATH_LIST-",
                          size=(30, 12),
                          right_click_menu=self.__right_click_menu,
                          horizontal_scroll=True)
            ]], visible=False)
        ],

        [sg.Frame("Негативный список папок",[
            [sg.B("Выбрать файлы и папки",
                  key="-BTN_NEGATIVE_PATH_LIST-")],
            [sg.Multiline(key="-MULTI_NEGATIVE_PATH_LIST-",
                          size=(30, 12),
                          right_click_menu=self.__right_click_menu,
                          horizontal_scroll=True)
            ]]),

        sg.Frame("Чёрный список папок",[
            [sg.B("Выбрать файлы и папки",
                  key="-BTN_BLACK_PATH_LIST-")],
            [sg.Multiline(key="-MULTI_BLACK_PATH_LIST-",
                          size=(30, 12),
                          right_click_menu=self.__right_click_menu,
                          horizontal_scroll=True)
            ]], visible=False)
        ]
        ]
        return sg.Frame(
            "Список путей папок, для сбора изображений, \nи нахождения по ним изображения",
            layout_folder_multiline_list)


    def _build_basic_launch_parameters_frame(self):
        layout_basic_launch_parameters = [
            [self._build_make_folder_list_frame(),
            self._build_clip_tools_frame()]
        ]
        return sg.Frame("", layout_basic_launch_parameters, size=(830, 350))

    def _build_make_folder_list_frame(self):
        layout_make_folder_list = [
                [sg.T("Запуск сбора изображений, \nи добавление в файловый список (json)")],
                [sg.Frame("",[[sg.T("shift + ` или shift + ё, останавливает сбор")]])],
                [sg.B(key="-BTN_FOLDER_MAKE_LIST-", button_text="Собрать все изображения")],
                [sg.Checkbox(key="-CHBX_SAVE_IMAGE_LIST-", text="Авто Сохранение", default=True)],
                [sg.Checkbox(key="-CHBX_APPEND_WHITE_LIST-", text='Добавление из белого списка', default=False)],
                [sg.Checkbox(key="-CHBX_FILTER_WORK_LIST-", text='Фильтр во время сбора', default=True)],
                [sg.T("Всего изображений: 0", key="-TEXT_COUNT_IMAGES-")],
                [sg.T("Всего обработанных изображений: 0", key="-TEXT_RESULT_COUNT_IMAGES-")],
                [sg.T(text="Сохранять через каждые"),
                sg.I(key="-SAVE_EVERY_N_JSON-", default_text=100, size=(10, 0)),
                sg.T(text="шагов")],
            ]
        return sg.Frame("", layout_make_folder_list, size=(400, 500))

    def _build_clip_tools_frame(self):
        layout_clip_tools = [
            [sg.Frame("",[[sg.T("shift + ` или shift + ё, останавливает обучение")]])],
            [sg.Push(),sg.B(key="-BTN_CLIP_TRAIN-", button_text="Начать обучать модель"),sg.Push()],
            [sg.Checkbox(key="-CHBX_CHECK_MODEL-", text="Проверить перед обучением, модель", default=True)],
            [sg.Checkbox(key="-CHBX_REPLACE_MODEL-", text="При начале обучении, обучается новая модель")]
        ]
        return sg.Frame("", layout_clip_tools)

    def _build_cleanup_images_find_frame(self):
        layout_cleanup_images_find = [
            [sg.Checkbox(key="-CHBX_CLEANUP_FIND_RES-", text="Автоматически удалять найденные изображения из папки images_find")]
        ]
        return sg.Frame("",layout_cleanup_images_find)


     # This function reads the events from the elements and returns the data
    def read_event(self):
        event, values = self._window.read()
        event_id = event[0] if event is not None else None
        return event_id, event, values

    def close(self):
        self._window.close()

    async def process_event(self, event, values):
        try: # Если по индексу event, в словаре не None, тогда присваиваем значение к переменной  value.
             # Иначе, переменную освобождаем, от присвоенных значений, value = None
            value = values[event]
        except Exception as e:
            value = None
            pass

        self._element = self._window.find_element_with_focus()

        # if self._element is None:
        #     continue  # Просто пропускаем итерацию, если элемента с фокусом нет

        if not isinstance(self._window.find_element_with_focus().widget, NoneType):
            self._widget = self._window.find_element_with_focus().widget
        else:
            print("отсутствует widget")


        if event == 'Выделить всё':
            try:
                self._widget.selection_clear()
                self._widget.tag_add('sel', '1.0', 'end')
            except:
                # print('Nothing selected')
                pass
        elif event == 'Копировать':
            try:
                text = self._widget.selection_get()
                self._window.TKroot.clipboard_clear()
                self._window.TKroot.clipboard_append(text)
            except:
                # print('Nothing selected')
                pass

        elif event == 'Вставить':
            self._widget.insert(sg.tk.INSERT, self._window.TKroot.clipboard_get())

        elif event == 'Вырезать':
            try:
                text = self._element.Widget.selection_get()
                self._window.TKroot.clipboard_clear()
                self._window.TKroot.clipboard_append(text)
                self._widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
            except:
                # print('Nothing selected')
                pass

        elif event == 'Удалить':
            try:
                self._widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
            except:
                # print('Nothing selected')
                pass

        elif event == "-FIBR_SEARCH_PATH-":
            self._window['-IN_TEXT_PATH-'].update(value)
            print(f"Выбираем изображение для поиска: {value}")


        elif event == "-FIBR_JSON_LOAD_PATH-":
            await asyncio.sleep(0)
            self._window['-IN_JSON_PATH-'].update(value)
            self.__IN_JSON_PATH = value
            print(f"Загружаем список путей изображений из: {value}")
            self.__gen_clip.image_list = load_json_file(self.__IN_JSON_PATH)
            print("Загрузка завершено")

        elif event == "-FIBR_JSON_SAVE_PATH-":
            await asyncio.sleep(0)
            self._window['-IN_JSON_PATH-'].update(value)
            self.__IN_JSON_PATH = value
            print(f"Сохраняем список путей изображений в: {value}")
            save_json_file(self.__gen_clip.image_list,self.__IN_JSON_PATH,indent=0)
            print("Сохранение завершено")

        elif event == "-FIBR_PKL_LOAD_PATH-":
            await asyncio.sleep(0)
            self._window['-IN_PKL_PATH-'].update(value)
            self.__IN_PKL_PATH = value
            print(f"Загружаем базу обработанных изображений из: {value}")
            self.__gen_clip.pickle_file = load_pkl(self.__IN_PKL_PATH)
            print("Загрузка завершено")

        elif event == "-FIBR_PKL_SAVE_PATH-":
            await asyncio.sleep(0)
            self._window['-IN_PKL_PATH-'].update(value)
            self.__IN_PKL_PATH = value
            print(f"Сохраняем базу обработанных изображений в: {value}")
            save_pkl(self.__gen_clip.pickle_file,self.__IN_PKL_PATH)
            print("Сохранение завершено")


        elif event == "-BTN_POSITIVE_PATH_LIST-":
            multilist = self._window["-MULTI_POSITIVE_PATH_LIST-"].get()
            try:
                files = '\n'.join(popup_paths(path=str(Path.cwd()), width=80))
            except TypeError:
                print("Ошибка. Не можем добавить. Поврежден файл, или папка")
                return None
            result = multilist+"\n"+files+"\n" if multilist != "" else multilist+files+"\n"
            await asyncio.sleep(0)
            self._window["-MULTI_POSITIVE_PATH_LIST-"].update(result)

        elif event == "-BTN_NEGATIVE_PATH_LIST-":
            multilist = self._window["-MULTI_NEGATIVE_PATH_LIST-"].get()
            try:
                files = '\n'.join(popup_paths(path=str(Path.cwd()), width=80))
            except TypeError:
                print("Ошибка. Не можем добавить. Поврежден файл, или папка")
                return None
            result = multilist+"\n"+files+"\n" if multilist != "" else multilist+files+"\n"
            await asyncio.sleep(0)
            self._window["-MULTI_NEGATIVE_PATH_LIST-"].update(result)

        elif event == "-BTN_WHITE_PATH_LIST-":
            multilist = self._window["-MULTI_WHITE_PATH_LIST-"].get()
            try:
                files = '\n'.join(popup_paths(path=str(Path.cwd()), width=80))
            except TypeError:
                print("Ошибка. Не можем добавить. Поврежден файл, или папка")
                return None
            result = multilist+"\n"+files+"\n" if multilist != "" else multilist+files+"\n"
            await asyncio.sleep(0)
            self._window["-MULTI_WHITE_PATH_LIST-"].update(result)

        elif event == "-BTN_BLACK_PATH_LIST-":
            multilist = self._window["-MULTI_BLACK_PATH_LIST-"].get()
            try:
                files = '\n'.join(popup_paths(path=str(Path.cwd()), width=80))
            except TypeError:
                print("Ошибка. Не можем добавить. Поврежден файл, или папка")
                return None
            result = multilist+"\n"+files+"\n" if multilist != "" else multilist+files+"\n"
            await asyncio.sleep(0)
            self._window["-MULTI_BLACK_PATH_LIST-"].update(result)


        elif event == "-UPDATE_SHOW_IMAGE_LIST_JSON-":
            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
            print(f'{self._window["-TEXT_COUNT_IMAGES-"].get()}')

        elif event == "-BTN_FOLDER_MAKE_LIST-":
            print("Собираем Изображения")



            self.__new_folder_list = self._window["-MULTI_POSITIVE_PATH_LIST-"].get().split("\n")
            self.__new_neg_folder_list = self._window["-MULTI_NEGATIVE_PATH_LIST-"].get().split("\n")
            self.__new_white_list = self._window["-MULTI_WHITE_PATH_LIST-"].get().split("\n")
            self.__new_black_list = self._window["-MULTI_BLACK_PATH_LIST-"].get().split("\n")
            self.__filter_work = filter_bool(self._window["-CHBX_FILTER_WORK_LIST-"].get())
            self.__append_white = filter_bool(self._window["-CHBX_APPEND_WHITE_LIST-"].get())
            self.__save_every_n_json = self.__widget_is_int(self._window,
                                                            "-SAVE_EVERY_N_JSON-",
                                                            True)




            print("Собираем")
            await asyncio.sleep(0)
            self._window.start_thread(
                lambda: self.__gen_clip.find_image_list(
                    self.__new_folder_list,
                    self.__new_neg_folder_list,
                    self.__new_white_list,
                    self.__new_black_list,
                    self.__filter_work,
                    self.__append_white,
                    self.__save_every_n_json,
                    window_PySimpleGUI=self._window,
                    get_widget_PySimpleGUI="-TEXT_COUNT_IMAGES-",
                    update_PySimpleGUI=f"Всего изображений: {len(self.__gen_clip.get_image_list())}"
                ),
                "-UPDATE_SHOW_IMAGE_LIST_JSON-"
            )

            BOOL_CHBX_SAVE_IMAGE_LIST = filter_bool(self._window['-CHBX_SAVE_IMAGE_LIST-'].get())
            print(f"Проверяем, Авто Сохранение: {BOOL_CHBX_SAVE_IMAGE_LIST}")
            if BOOL_CHBX_SAVE_IMAGE_LIST:
                print(f"Проверяем на существование файла: {self.__IN_JSON_PATH}"
                      f"\nСуществует файл: {os.path.isfile(self.__IN_JSON_PATH)}")
                if not os.path.isfile(self.__IN_JSON_PATH):
                    print(f"Создаём: {self.__IN_JSON_PATH}")
                    isdir_makefolder("\\".join(self.__IN_JSON_PATH.split("\\")[:-1]))
                print(f"Сохраняю список путей изображений в json файл: {self.__IN_JSON_PATH}")
                print(f"Колличество изображений в списке: {len(self.__gen_clip.image_list)}")
                save_json_file(self.__gen_clip.image_list,self.__IN_JSON_PATH, indent=0)

            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
            print(f'{self._window["-TEXT_COUNT_IMAGES-"].get()}')


        elif event == "-RESULT_SHOW_IMAGES-":
            print(f"Переходим: {PATH_SEARCH_RES}")
            isdir_makefolder(PATH_SEARCH_RES)
            open_folder_in_explorer(PATH_SEARCH_RES)

        elif event == "-BTN_CLIP_TRAIN-":
            print("Начинаем обучать модель на собранных изображений")

            print("run started")
            # Определяем устройство для выполнения операций
            self.__device = "cuda" if torch.cuda.is_available() else "cpu"
            self.__gen_clip.device = self.__device
            # Выводим информацию о выбранном устройстве
            print("device:", self.__device)

            self.__replace_model = filter_bool(self._window['-CHBX_REPLACE_MODEL-'].get())

            # Проверяем, нужно ли заменить модель и предобработку
            if self.__replace_model or (self.__gen_clip.model == None or self.__gen_clip.preprocess == None):
                print("Создаём модель и препроцессор")
                # Выводим сообщение о создании модели и препроцессоре
                print(f"Создаём модель и препроцессор, загружаем clip: {CLIP_LOAD}")
                # Загружаем модель и предобработку
                self.__model, self.__preprocess = clip.load(CLIP_LOAD)

                self.__gen_clip.preprocess = self.__preprocess
                self.__gen_clip.model = self.__model



            # Устанавливаем частоту сохранения результатов
            self.__save_every_n = 100

            if self.__gen_clip.get_image_list() != None:
                print(fr"Всего изображений {len(self.__gen_clip.get_image_list())}")
            if self.__gen_clip.pickle_file != None:
                print(f"Обработанно изображений: {len(self.__gen_clip.pickle_file)}")

            self.__check_image_paths = filter_bool(self._window['-CHBX_CHECK_MODEL-'].get())


            # Создаём векторные представления изображений
            print("Создаём векторные представления изображений")
            await asyncio.sleep(0)
            self._window.start_thread(
                lambda: self.__gen_clip.create_clip_image_features(
                    self.__gen_clip.pickle_file,
                    self.__gen_clip.image_list,
                    self.__save_every_n,
                    self.__check_image_paths
                )
            )
            # self.__gen_clip.create_clip_image_features(self.__gen_clip.pickle_file, self.__gen_clip.image_list,self.__save_every_n)

            print("create_clip_image_features finished")


        elif event == "-BTN_SEARCH_TEXT-":
            if not isinstance(self.__gen_clip.pickle_file, NoneType):
                if len(self.__gen_clip.pickle_file) == 0:
                    print("Пожалуйста, обучите модель, а затем ищите по тексту")
                    return None
            elif not os.path.isfile(self.__IN_PKL_PATH):
                if len(load_pkl(self.__IN_PKL_PATH)) == 0:
                    print("Пожалуйста, обучите модель, а затем ищите по тексту")
                    return None

            if filter_bool(self._window["-CHBX_CLEANUP_FIND_RES-"].get()):
                self.__cleanup_temp()

            self._result_quantity_images = self.__widget_is_int(self._window,
                                                                "-RESULT_QUANTITY_IMAGES_OUT-",
                                                                update_widget=True)

            self.__gen_clip.searcher_clip(len_count=self._result_quantity_images,
                                          query_str_pillow=str(self._window["-IN_TEXT_PATH-"].get()),
                                          is_str=True,
                                          image_filenames=self.__gen_clip.image_list,
                                          image_features=self.__gen_clip.pickle_file,
                                          path_clip_image=self.__IN_PKL_PATH,
                                          file_names_path=self.__IN_JSON_PATH)

        elif event == "-BTN_SEARCH_PATH-":
            if not isinstance(self.__gen_clip.pickle_file, NoneType):
                if len(self.__gen_clip.pickle_file) == 0:
                    print("Пожалуйста, обучите модель, а затем ищите по изображению")
                    return None
            elif not os.path.isfile(self.__IN_PKL_PATH):
                if len(load_pkl(self.__IN_PKL_PATH)) == 0:
                    print("Пожалуйста, обучите модель, а затем ищите по изображению")
                    return None

            if filter_bool(self._window["-CHBX_CLEANUP_FIND_RES-"].get()):
                self.__cleanup_temp()

            self.__gen_clip.searcher_clip(len_count=int(self._window["-RESULT_QUANTITY_IMAGES_OUT-"].get()),
                                          query_image_pillow=str(self._window["-IN_TEXT_PATH-"].get()),
                                          is_str=False,
                                          image_filenames=self.__gen_clip.image_list,
                                          image_features=self.__gen_clip.pickle_file,
                                          path_clip_image=self.__IN_PKL_PATH,
                                          file_names_path=self.__IN_JSON_PATH)



    def __cleanup_temp(self):
        temp_dir = PATH_SEARCH_RES
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

    def __widget_is_int(self,window, get_widget, update_widget=False, return_res=True):
        if not isfloat(window[get_widget].get()):
            self._value_int_temp = re.sub(r'[^0-9]', "", window[get_widget].get())
            if not isfloat(self._value_int_temp) or self._value_int_temp == 0:
                self._value_int_temp = 100
            if update_widget:
                window[get_widget].update(self._value_int_temp)
        else:
            print(window[get_widget].get())
            self._value_int_temp = int(window[get_widget].get())
            if self._value_int_temp == 0:
                self._value_int_temp = 100
            else:
                self._value_int_temp = int(window[get_widget].get())
        if return_res:
            return int(self._value_int_temp)
        else:
            return None

        # if event == 'Копировать' and self._widget.select_present():
        #     text = self._widget.selection_get()
        #     self._window.TKroot.clipboard_clear()
        #     self._window.TKroot.clipboard_append(text)
        #
        # elif event == 'Вырезать' and self._widget.select_present():
        #     text = self._widget.selection_get()
        #     self._window.TKroot.clipboard_clear()
        #     self._window.TKroot.clipboard_append(text)
        #     self._widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
        #
        # elif event == 'Вставить':
        #     if self._widget.select_present():
        #         self._widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
        #     self._widget.insert(sg.tk.INSERT, self._window.TKroot.clipboard_get())
        #
        # elif event == 'Удалить' and self._widget.select_present():
        #     self._widget.delete(sg.tk.SEL_FIRST, sg.tk.SEL_LAST)
        #
        # else:
        # self.process_event(event)

    # https://github.com/PySimpleGUI/PySimpleGUI/issues/6193
    def __validate_integer(self,text):
        value = 0
        if text:
            try:
                value = int(text)
            except ValueError:
                value = 100
        return True if 0 <= value <= 1000000 else False  # Return True if valid input


# Запуск программы
async def start_run():
    gui_image_search = Main_gui_image_search()

    # Event loop
    while True:
        event_id, event, values = gui_image_search.read_event()

        # print(event_id, event, values)

        if event_id in {sg.WIN_CLOSED}:
            break

        await gui_image_search.process_event(event,values)

    gui_image_search.close()