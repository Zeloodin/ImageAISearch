""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""
from deep_translator import GoogleTranslator
# GoogleTranslator не требует ключа

from core.tools import bool_tools

def mini_translator(text, to_lang='auto', from_lang="en"):
    try:
        if to_lang == from_lang:
            return text
        translator = GoogleTranslator(to_lang, from_lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(e)
        return text

def reverse_item(item):
    return item[::-1]

def remove_duplicates(item, mode = "", reverse = False, ext = "str", sep = ""):
    if bool_tools.filter_bool(reverse):
        item = reverse_item(item)

    if mode.lower() == "lower" or mode.lower() == "l" or mode.lower().startswith("l"):
        res = list(dict.fromkeys(item.lower()))

    elif mode.lower() == "upper" or mode.lower() == "u" or mode.lower().startswith("u"):
        res = list(dict.fromkeys(item.upper()))

    elif mode.lower() == "capitalize" or mode.lower() == "c" or mode.lower().startswith("c"):
        res = list(dict.fromkeys(item.capitalize()))

    else:
        res = list(dict.fromkeys(item))


    if bool_tools.filter_bool(reverse):
        res = reverse_item(res)


    if ext.lower() == "str" or ext.lower() == "s" or ext.lower().startswith("s"):
        return sep.join(res)

    elif ext.lower() == "tuple" or ext.lower() == "t" or ext.lower().startswith("t"):
        return tuple(res)

    elif ext.lower() == "list" or ext.lower() == "lst" or ext.lower() == "l" or ext.lower().startswith("l"):
        return res

    else:
        return res