""" -*- coding: UTF-8 -*-
handle msg between js and python side
"""

from inspect import currentframe
def retrieve_name(var):
    callers_local_vars = currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]