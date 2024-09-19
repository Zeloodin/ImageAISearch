import PySimpleGUI as sg
from scipy.constants import value


from core.simple_gui_interface.main_sgi import start_run

if __name__ == "__main__":
    start_run()


    # import PySimpleGUI as sg
    # # event, values = sg.Window('Window Title').Layout(
    # #     [[sg.Input(key='_FILES_'), sg.FilesBrowse()], [sg.OK(), sg.Cancel()]]).Read()
    # #
    # # print("\n".join(values['_FILES_'].split(';')))
    #
    # # files = sg.popup_get_file('Unique File select', multiple_files=True)
    # files = sg.popup_get_folder('Unique Folder select')
    # print("\n".join(files.split(';')))

