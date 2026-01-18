import os
import customtkinter
import webbrowser
import json
from util.gui_util import GuiUtil

gui = GuiUtil()

def find(path : str, name: str):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root,name)

def font(size : int):
    return customtkinter.CTkFont(family="Arial",size=size)


def open_url(url):
    webbrowser.open(url)

def save_file(path: str, file : str, data : object) -> None:
    try:
        for root, dirs, files in os.walk(path):
            with open(file,'w') as file:
                json.dump(data,file)
    except Exception as e:
        # TODO: FIX DIALOG
        gui.show_dialog("Error", "cancel", "Failed to save file", "OK")

def read_json_file(path: str, filename: str) -> any :
    try:
        full_path = os.path.join(path, filename)
        with open(full_path,'r') as file:
            return json.load(file)
    except Exception as e:
        gui.show_dialog("Error", "cancel", "Failed to read file", "OK")
        return None

