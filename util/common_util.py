import os
import customtkinter
import webbrowser
import json
from util.gui_util import GuiUtil
from datetime import datetime , timezone
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
        GuiUtil().show_dialog("Error", "cancel", "Failed to save file", "OK")

def read_json_file(path: str, filename: str) -> any :
    try:
        full_path = os.path.join(path, filename)
        with open(full_path,'r') as file:
            return json.load(file)
    except Exception as e:
        GuiUtil().show_dialog("Error", "cancel", "Failed to read file", "OK")
        return None


def date_str_to_iso(date_str) -> str:
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"