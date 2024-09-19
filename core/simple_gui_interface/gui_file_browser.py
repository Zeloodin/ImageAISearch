from pathlib import Path
import PySimpleGUI as sg
import psutil

# https://github.com/PySimpleGUI/PySimpleGUI/issues/4393
def popup_paths(path=Path.home(), width=60):
    sg.set_options(font=("Courier New", 14))
    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'
    DISK_LIST = ["".join(dsk[:1]) for dsk in psutil.disk_partitions()]

    def short(file, width):
        return file[:width // 2 - 3] + '...' + file[-width // 2:] if len(file) > width else file

    def create_win(path):
        files = sorted(sorted(Path(path).iterdir()), key=lambda x: Path(x).is_file())
        treedata = sg.TreeData()
        for i, file in enumerate(files):
            f = str(file)
            treedata.insert("", i, short(f, width - 8), [f], icon=folder_icon if Path(f).is_dir() else file_icon)
        layout = [
            [sg.Tree(data=treedata, headings=['Notes', ], pad=(0, 0),
                     show_expanded=True, col0_width=width, auto_size_columns=False,
                     visible_column_map=[False, ], select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                     num_rows=15, row_height=20, font=('Courier New', 14), key="TREE")],
            [sg.Button('OK'), sg.Button('Cancel'), sg.Button('UP'),
             sg.Combo(DISK_LIST,
                      key="-SELECT_DISK-",
                      enable_events=True,
                      default_value="".join(path[:1]))],
        ]
        window = sg.Window("Select files or directories", layout, modal=True, finalize=True)
        tree = window['TREE']
        tree.Widget.configure(show='tree')  # Hide Tree Header
        tree.bind("<Double-1>", "_DOUBLE_CLICK")
        while True:
            event, values = window.read()
            if event == 'TREE_DOUBLE_CLICK':
                if values['TREE'] != []:
                    value = values['TREE'][0]
                    path = treedata.tree_dict[value].values[0]
                    if Path(path).is_dir():
                        result = path
                        break
                continue
            elif event in (sg.WINDOW_CLOSED, 'Cancel'):
                result = []
            elif event == 'OK':
                result = [treedata.tree_dict[i].values[0] for i in values['TREE']]
            elif event == 'UP':
                result = str(Path(path).parent)

            elif event == "-SELECT_DISK-":
                path = values['-SELECT_DISK-']
                result = str(Path(path).parent)

            break
        window.close()
        return result

    while True:
        result = create_win(path)
        if isinstance(result, str):
            path = result
        else:
            break
    return result



# sg.theme('DarkBlue3')
#
#
# layout = [[sg.Button("Browse")]]
#
# window = sg.Window('title', layout)
#
# while True:
#     event, values = window.Read()
#     if event == sg.WINDOW_CLOSED:
#         break
#     elif event == 'Browse':
#         files = popup_paths(path='D:/', width=80)
#         print(files)
#
# window.close()