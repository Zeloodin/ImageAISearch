""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""
from PIL import Image
from pathlib import Path

# TODO
# Нужно переделать с ..\\..\\ на расположенние пути run.py
# Или рядом с venv, где в папке находится, папка venv.
CWD_PATH = str(Path.cwd())+"\\" # str(Path.cwd())+"\\..\\..\\"
PATH_DATA = CWD_PATH+"data"+"\\"
PATH_SEARCH_RES = PATH_DATA+"images_find"+"\\"

PKL_FILE_PATH = PATH_DATA+"clip_image_features.pkl"
JSON_FILE_PATH = PATH_DATA+"sample.json"
TEMP_VAL = []
EMPTY_LIST = []
CLIP_LOAD = "ViT-B/32"
# ['RN50', 'RN101', 'RN50x4', 'RN50x16', 'RN50x64', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14', 'ViT-L/14@336px']

IMG_EXTS = Image.registered_extensions()
# supported_extensions
IMG_SUP_EXTS = tuple(ex for ex, f in IMG_EXTS.items() if f in Image.OPEN)
IMG_FILE_TYPES = (tuple(('Images', f"*{ex}*") for ex in
                        ('.png', '.apng', '.bmp', '.jfif', '.jpe', '.jpeg', '.tif', '.tiff', '.tga', '.tga', '.webp'))+
                  # (tuple((f, f"*{ex}*") for ex, f  in Image.registered_extensions().items())) +
                  (("ALL Files", "*"),))
JSON_FILE_TYPES = (("Json files", "*.json*"), ("ALL Files", "*"))
PKL_FILE_TYPES = (("Pickle files", "*.pkl*"), ("ALL Files", "*"))
