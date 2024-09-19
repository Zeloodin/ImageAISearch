import subprocess                                # Импортируем модуль subprocess

def open_folder_in_explorer(path_in_explorer):   # Определяем функцию open_folder_in_explorer
    path_in_explorer = str(path_in_explorer)     # Приводим путь к строковому типу
    try:                                         # Попытка выполнения команды
        print(path_in_explorer)                  # Выводим переданный путь в консоль
        command = ["explorer", path_in_explorer] # Формируем команду для открытия папки через explorer
        subprocess.run(command)                  # Запускаем команду с помощью subprocess.run()
    except Exception as e:                       # Обрабатываем исключения
        print(e)                                 # Выводим информацию об ошибке
        print(path_in_explorer)                  # Выводим переданный путь в консоль для отладки