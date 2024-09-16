#!/usr/bin/env python
""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

from core.tools.folder_tools import \
    (filter_str_list,
     search_in_list,
     Folder_make_list,
     isdir_makefolder)

from core.tools.specific import retrieve_name
from core.tools.bool_tools import filter_bool, isfloat
from core.tools.list_tools import remove_duplicates, reverse_item, mini_translator
from core.tools.json_tools import save_json_file, load_json_file

from core.tools.variables import (
    CWD_PATH,
    PATH_DATA,
    PATH_SEARCH_RES,
    PKL_FILE_PATH,
    JSON_FILE_PATH,
    TEMP_VAL,
    EMPTY_LIST,
    CLIP_LOAD
)