""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

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
# ['RN50', 'RN101', 'RN50x4', 'RN50x16', 'RN50x64', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14', 'ViT-L/14@336px']

