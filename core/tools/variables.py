from pathlib import Path

from core.tools.folder_tools import isdir_makefolder

# TODO
# Нужно переделать с ..\\..\\ на расположенние пути run.py
# Или рядом с venv, где в папке находится, папка venv.
CWD_PATH = str(Path.cwd())+"\\..\\..\\"
PATH_DATA = CWD_PATH+"data"+"\\"
PATH_SEARCH_RES = PATH_DATA+"images_find"+"\\"

PKL_FILE_PATH = PATH_DATA+"clip_image_features.pkl"
JSON_FILE_PATH = PATH_DATA+"sample.json"
TEMP_VAL = []
EMPTY_LIST = []
CLIP_LOAD = "ViT-B/32"

