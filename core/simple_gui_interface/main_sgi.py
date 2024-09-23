import os
import shutil
from pathlib import Path
import PySimpleGUI as sg
import torch
from clip import clip
import re
from types import NoneType
from time import sleep

from keyboard import add_hotkey # В случае, когда надо отключить
import asyncio # Во время выполнения, асинхронно выполняет, рядом с другими задачами

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

        self.__tabs_mode = "tab_text"

        # Код прерывает цикл, в _from_folder И _for_folder И negative_filter
        try:
            # Если Английская расскладка, то код будет выполниться правильно.
            add_hotkey("ctrl + q", lambda: asyncio.run(self.__exit_return_break("ctrl + q")))
        except ValueError:
            # Если Русская расскладка, то код будет выполниться, после try except ValueError.
            add_hotkey("ctrl + й", lambda: asyncio.run(self.__exit_return_break("ctrl + й")))
        # На других расскладках не проверялись.


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
            [[sg.Push()],
             sg.Frame("",[[sg.Push(), self._build_search_frame()],
                         [sg.Push(), self._build_make_folder_list_frame()]]),
             self._build_folder_multiline_list_frame()],
            [sg.T("В случае если хотите остановить сканирование, поиск\nудерживайте клавиши Ctrl + Q, для остановки")]]
        self._window = sg.Window(
            title="ImageAISearch",
            layout=self._layout_main,
            finalize=True,
            margins=(10, 10),
            font=(None,12))

        # self._window["-TEXT_COUNT_IMAGES-"].set_focus()
        # self._window["-BTN_FOLDER_MAKE_LIST-"].set_focus()
        # self._window["-BTN_POSITIVE_PATH_LIST-"].set_focus()
        # self._window["-BTN_NEGATIVE_PATH_LIST-"].set_focus()
        # self._window["-RESULT_SHOW_IMAGES-"].set_focus()
        # self._window["-RESULT_QUANTITY_IMAGES_OUT-"].set_focus()
        # self._window["-FIBR_SEARCH_PATH-"].set_focus()
        # self._window["-BTN_SEARCH_PATH-"].set_focus()
        # self._window["-BTN_SEARCH_TEXT-"].set_focus()
        # self._window["-TEXT_RESULT_COUNT_IMAGES-"].set_focus()

        # Раньше это работало отлично.
        # Сейчас, это перестало работать
        # При других символах, будет вызываться ошибка.
        # Надо в таких случаях, или выдавать ошибку в консоль, или заменять всё на ничего, кроме чисел.
        # Внимание, Сохранять каждые 0 шагов, вызовет ошибку. Это надо запомнить.
        self._vcmd = (self._window.TKroot.register(self.__validate_integer), '%P')
        self._window['-RESULT_QUANTITY_IMAGES_OUT-'].widget.configure(validate='all', validatecommand=self._vcmd)


        if self.__gen_clip.image_list:
            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
        else:
            if self.__gen_clip.pickle_file:
                self.__gen_clip.image_list = [n.get("image_id") for n in self.__gen_clip.pickle_file]
                self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
                save_json_file(self.__gen_clip.image_list, self.__IN_JSON_PATH)

        if self.__gen_clip.pickle_file:
            self._window["-TEXT_RESULT_COUNT_IMAGES-"].update(f"Всего обработанно изображений: {len(self.__gen_clip.pickle_file)}")

        print("run started")
        # Определяем устройство для выполнения операций
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        self.__gen_clip.device = self.__device
        # Выводим информацию о выбранном устройстве
        print("device:", self.__device)

    #
    #         self._layout_main = [
    #             [sg.TabGroup(
    #                 [[sg.Tab("Tab 1", ),
    #                   sg.Tab("Tab 2", )]])]]


    def _build_search_frame(self):
        layout_text =  [[sg.Frame("Текст",
                                  [[sg.T("Введите описание текста")],
                                  [sg.I(key="-IN_TEXT-", right_click_menu=self.__right_click_menu,font=(None, 18))],

                                  [sg.B(key="-BTN_SEARCH_TEXT-", button_text="Поиск по описанию")]]
                                  )
                         ]]

        layout_image = [[sg.Frame("Картинки",
                                  [[sg.T("Введите путь к картинке, или нажмите Выбрать картинку")],
                                  [sg.I(key="-IN_TEXT_PATH-", right_click_menu=self.__right_click_menu,font=(None, 18))],

                                  [sg.B(key="-BTN_SEARCH_PATH-", button_text="Поиск по картинке"),

                                  sg.I(key="-FIBR_SEARCH_PATH-", visible=False, size=(0, 0), disabled=True,
                                       enable_events=True),
                                  sg.FileBrowse(  # key="-FIBR_SEARCH_PATH-",
                                      button_text="Выбрать картинку",
                                      # enable_events=True,
                                      file_types=IMG_FILE_TYPES
                                  )]]
                                  )
                         ]]



        layout_search = [

            [sg.Push(),

            sg.TabGroup([[sg.Tab("Текст", layout_text, key= "tab_text"),
                          sg.Tab("Картинки", layout_image, key= "tab_image")]],
                         enable_events=True, key= "tab_group"),
            sg.Push()],

            [sg.Push(), sg.Frame("",[
            [sg.T(text="Показать"),
            sg.I(key="-RESULT_QUANTITY_IMAGES_OUT-", default_text=10, size=(10, 0)),
            sg.T(text="найденных изображений")],
            [sg.B(key="-RESULT_SHOW_IMAGES-", button_text="Показать результат")]
            ]), sg.Push()],
            [self._build_cleanup_images_find_frame()]
        ]
        return sg.Frame("Поисковой запрос", layout_search)

    def _build_folder_multiline_list_frame(self):
        layout_folder_multiline_list = [
        [sg.Frame("Список папок изображений",[
            [sg.B("Выбрать файлы и папки",
                  key="-BTN_POSITIVE_PATH_LIST-")],
            [sg.Multiline(key="-MULTI_POSITIVE_PATH_LIST-",
                          size=(30, 12),
                          right_click_menu=self.__right_click_menu,
                          horizontal_scroll=True)
            ]])],

        [sg.Frame("Негативный список папок",[
            [sg.B("Выбрать файлы и папки",
                  key="-BTN_NEGATIVE_PATH_LIST-")],
            [sg.Multiline(key="-MULTI_NEGATIVE_PATH_LIST-",
                          size=(30, 12),
                          right_click_menu=self.__right_click_menu,
                          horizontal_scroll=True)
            ]])]
        ]
        return sg.Frame(
            "Список путей папок, для сбора изображений, \nи нахождения по ним изображения",
            layout_folder_multiline_list)

    def _build_make_folder_list_frame(self):
        layout_make_folder_list = [
                [sg.T("Запуск сбора изображений, \nи добавление в файловый список")],
                [sg.B(key="-BTN_FOLDER_MAKE_LIST-", button_text="Сканировать")],
                [sg.T("Всего изображений: 0", key="-TEXT_COUNT_IMAGES-")],
                [sg.T("Всего обработанно изображений: 0", key="-TEXT_RESULT_COUNT_IMAGES-")],
            ]
        return sg.Frame("", layout_make_folder_list)

    def _build_cleanup_images_find_frame(self):
        layout_cleanup_images_find = [
            [sg.Checkbox(key="-CHBX_CLEANUP_FIND_RES-", text="Автоматически удалять найденные изображения из папки images_find")]
        ]
        return sg.Frame("",layout_cleanup_images_find)


     # This function reads the events from the elements and returns the data
    def read_event(self):
        event, values = self._window.read()
        # print(event)

        if event is not None:
            event_id = event[0]
        else:
            event_id = None


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

        try:
            if not isinstance(self._window.find_element_with_focus().widget, NoneType):
                self._widget = self._window.find_element_with_focus().widget
            else:
                print("отсутствует widget")
        except Exception as e:
            # print(e)
            pass


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

        elif event == "tab_group":
            print(self._window["tab_group"].get())

        elif event == "tab_text":
            self.__tabs_mode = "tab_text"
        elif event == "tab_image":
            self.__tabs_mode = "tab_image"


        elif event == "-FIBR_SEARCH_PATH-":
            self._window['-IN_TEXT_PATH-'].update(value)
            print(f"Выбираем изображение для поиска: {value}")

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

        elif event == "-UPDATE_SHOW_IMAGE_LIST_JSON-":
            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
            print(f'{self._window["-TEXT_COUNT_IMAGES-"].get()}')

        elif event == "-BTN_FOLDER_MAKE_LIST-":

            print("Собираем, сканируем изображения")

            self.__new_folder_list = self._window["-MULTI_POSITIVE_PATH_LIST-"].get().split("\n")
            self.__new_neg_folder_list = self._window["-MULTI_NEGATIVE_PATH_LIST-"].get().split("\n")

            print("Собираем")
            await asyncio.sleep(0)
            self._window.start_thread(
                lambda: self.__gen_clip.find_image_list(
                    self.__new_folder_list,
                    self.__new_neg_folder_list,
                    filter_work=True,
                    append_white=False,
                    save_every_n=500,
                    window_PySimpleGUI=self._window,
                    get_widget_PySimpleGUI="-TEXT_COUNT_IMAGES-",
                    update_PySimpleGUI=f"Всего изображений: {len(self.__gen_clip.get_image_list())}"
                )
            ,"-BTN_TRAIN_MODEL-"
            )
            await asyncio.sleep(0)

            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
            print(f'{self._window["-TEXT_COUNT_IMAGES-"].get()}')

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

        elif event == "-BTN_TRAIN_MODEL-":

            print("Начинаем обучать модель на собранных изображений")

            print("run started")
            # Определяем устройство для выполнения операций
            self.__device = "cuda" if torch.cuda.is_available() else "cpu"
            self.__gen_clip.device = self.__device
            # Выводим информацию о выбранном устройстве
            print("device:", self.__device)

            # Проверяем, нужно ли заменить модель и предобработку
            if (self.__gen_clip.model == None or self.__gen_clip.preprocess == None):
                print("Создаём модель и препроцессор")
                # Выводим сообщение о создании модели и препроцессоре
                print(f"Создаём модель и препроцессор, загружаем clip: {CLIP_LOAD}")
                # Загружаем модель и предобработку
                self.__model, self.__preprocess = clip.load(CLIP_LOAD)

                self.__gen_clip.preprocess = self.__preprocess
                self.__gen_clip.model = self.__model

            if self.__gen_clip.get_image_list() != None:
                print(fr"Всего изображений {len(self.__gen_clip.image_list)}")
            if self.__gen_clip.pickle_file != None:
                print(f"Обработанно изображений: {len(self.__gen_clip.pickle_file)}")

            # Создаём векторные представления изображений
            print("Создаём векторные представления изображений")
            await asyncio.sleep(0)
            self._window.start_thread(
                lambda: self.__gen_clip.create_clip_image_features(
                    self.__gen_clip.pickle_file,
                    self.__gen_clip.image_list,
                    500,
                    True
                )
            ,"-UPDATE_COUNTS_IMAGES-"
            )

            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
            print(f'{self._window["-TEXT_COUNT_IMAGES-"].get()}')
            self._window["-TEXT_RESULT_COUNT_IMAGES-"].update(f"Всего обработанно изображений: {len(self.__gen_clip.pickle_file)}")
            print(f'{self._window["-TEXT_RESULT_COUNT_IMAGES-"].get()}')

            print("Сканирование завершено!")

        elif event == "-UPDATE_COUNTS_IMAGES-":
            self._window["-TEXT_COUNT_IMAGES-"].update(f"Всего изображений: {len(self.__gen_clip.image_list)}")
            self._window["-TEXT_RESULT_COUNT_IMAGES-"].update(f"Всего обработанно изображений: {len(self.__gen_clip.pickle_file)}")


        elif event == "-RESULT_SHOW_IMAGES-":
            if self.__tabs_mode == "tab_text":
                self.__in_text = str(self._window["-IN_TEXT-"].get())
                self.__in_text = str(re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9-.,_ ]', "", self.__in_text))
                if os.path.isdir(PATH_SEARCH_RES+self.__in_text):
                    print(f"Переходим: {PATH_SEARCH_RES+self.__in_text}")
                    isdir_makefolder(PATH_SEARCH_RES+self.__in_text)
                    open_folder_in_explorer(PATH_SEARCH_RES+self.__in_text)
                else:
                    print(f"Переходим: {PATH_SEARCH_RES}")
                    isdir_makefolder(PATH_SEARCH_RES)
                    open_folder_in_explorer(PATH_SEARCH_RES)
            else:
                print(f"Переходим: {PATH_SEARCH_RES}")
                isdir_makefolder(PATH_SEARCH_RES)
                open_folder_in_explorer(PATH_SEARCH_RES)


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

            # Проверяем, загружена модель, или нет, если нет, надо загрузить
            if (self.__gen_clip.model == None or self.__gen_clip.preprocess == None):
                print("Создаём модель и препроцессор")
                # Выводим сообщение о создании модели и препроцессоре
                print(f"Создаём модель и препроцессор, загружаем clip: {CLIP_LOAD}")
                # Загружаем модель и предобработку
                self.__model, self.__preprocess = clip.load(CLIP_LOAD)

                self.__gen_clip.preprocess = self.__preprocess
                self.__gen_clip.model = self.__model

            self._window.start_thread(
                lambda: self.__gen_clip.searcher_clip(len_count=self._result_quantity_images,
                                                  query_str_pillow=str(self._window["-IN_TEXT-"].get()),
                                                  is_str=True,
                                                  image_filenames=self.__gen_clip.image_list,
                                                  image_features=self.__gen_clip.pickle_file)
            )

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

                # Проверяем, загружена модель, или нет, если нет, надо загрузить
                if (self.__gen_clip.model == None or self.__gen_clip.preprocess == None):
                    print("Создаём модель и препроцессор")
                    # Выводим сообщение о создании модели и препроцессоре
                    print(f"Создаём модель и препроцессор, загружаем clip: {CLIP_LOAD}")
                    # Загружаем модель и предобработку
                    self.__model, self.__preprocess = clip.load(CLIP_LOAD)

                    self.__gen_clip.preprocess = self.__preprocess
                    self.__gen_clip.model = self.__model
            self._window.start_thread(
                lambda: self.__gen_clip.searcher_clip(len_count=int(self._window["-RESULT_QUANTITY_IMAGES_OUT-"].get()),
                                                  query_image_pillow=str(self._window["-IN_TEXT_PATH-"].get()),
                                                  is_str=False,
                                                  image_filenames=self.__gen_clip.image_list,
                                                  image_features=self.__gen_clip.pickle_file,
                                                  path_clip_image=self.__IN_PKL_PATH,
                                                  file_names_path=self.__IN_JSON_PATH)
            )


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

    async def __exit_return_break(self,key): # __on_callback
        for _ in range(10):
            self.__ex_return = True
            sleep(0.01)
        # print('pressed', key)
        # await asyncio.sleep(1)
        # print('end for', key)

    # https://github.com/PySimpleGUI/PySimpleGUI/issues/6193
    def __validate_integer(self,text):
        value = 0
        if text:
            try:
                value = int(text)
            except ValueError:
                value = -1
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