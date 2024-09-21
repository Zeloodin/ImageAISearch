import PySimpleGUI as sg
from scipy.constants import value
import asyncio

from core.simple_gui_interface.main_sgi import start_run

if __name__ == "__main__":
    asyncio.run(start_run())