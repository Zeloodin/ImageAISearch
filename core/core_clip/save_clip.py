import pickle as pk

from core.tools.variables import PKL_FILE_PATH

def save_pkl(all_image, filename = PKL_FILE_PATH):
    pk.dump(all_image, open(filename, "wb"))