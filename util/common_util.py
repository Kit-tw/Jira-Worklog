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

def check_directory(path : str):
    if not os.path.isdir(path):
        return create_directory(path)
    
def create_directory(path : str):
    try:
        os.mkdir(path)
        print(path)
        print("create directory success")
    except Exception as e:
        print(e)
        GuiUtil().show_dialog("Error", "cancel", f"Cannot create direcotry at {path}", "OK")
def font(size : int):
    return customtkinter.CTkFont(family="Arial",size=size)


def open_url(url):
    webbrowser.open(url)

def save_file(path: str, file : str, data : object) -> None:
    try:
        check_directory(path)
        full_path = os.path.join(path,file)
        with open(full_path,'w') as file:
            json.dump(data,file)
    except Exception as e:
        print(e)
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
