import os
import customtkinter
import webbrowser
import json
import shutil
from util.gui_util import GuiUtil
from datetime import datetime , timezone
import requests
from requests.auth import HTTPBasicAuth
from constant.Enum import (STORAGE)
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
        GuiUtil().show_dialog("Error", "cancel", f"Cannot create direcotry at {path}", options="OK")



def open_url(url):
    webbrowser.open(url)

def save_file(path: str, file : str, data : object, showDialog : bool = True) -> None:
    try:
        check_directory(path)
        full_path = os.path.join(path,file)
        with open(full_path,'w') as file:
            json.dump(data,file)
            if(showDialog):
                GuiUtil().show_dialog("Success", "check", f"file has been saved at {full_path}", options="OK")
    except Exception as e:
        print(e)
        GuiUtil().show_dialog("Error", "cancel", "Failed to save file", options="OK")

def delete_file(path: str, file: str):
    try:
        full_path = os.path.join(path, file)
        if os.path.isfile(full_path):
            os.remove(full_path)
            GuiUtil().show_dialog("Success", "check", f"file '{file}' has been deleted from {path}", options="OK")
        else:
            GuiUtil().show_dialog("Error", "cancel", f"file '{file}' not found in {path}", options="OK")
    except Exception as e:
        print(e)
        GuiUtil().show_dialog("Error", "cancel", "Failed to delete file", options="OK")

def read_json_file(path: str, filename: str) -> any :
    try:
        full_path = os.path.join(path, filename)
        with open(full_path,'r') as file:
            return json.load(file)
    except Exception as e:
        GuiUtil().show_dialog("Error", "cancel", "Failed to read file", options="OK")
        return None


def date_str_to_iso(date_str) -> str:
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"

def copy_file(src : str, dest : str):
    try:
        shutil.copyfile(src, dest)
        GuiUtil().show_dialog("Success","check", f"successfully copied to '{dest}'", options="OK")
    except shutil.SameFileError:
        GuiUtil().show_dialog("Error","cancel","Source and destination represent the same file.", options="OK")
    except PermissionError:
        GuiUtil().show_dialog("Error","cancel","Permission denied.", options="OK")
    except FileNotFoundError:
        GuiUtil().show_dialog("Error","cancel","Source file not found.", options="OK")
    except Exception as e:
        GuiUtil().show_dialog("Error","cancel",f"An error occurred: {e}", options="OK")


def get_user(email,api,prefix):
    url = f"https://{prefix}.atlassian.net/rest/api/3/myself"
    auth = HTTPBasicAuth(email, api)
    headers = {
    "Accept": "application/json"
    }
    return requests.request("GET",url,headers=headers,auth=auth)

#TODO : DELETE if at start of the month / user click clear history 
def get_worklog_history():
    if(find(STORAGE.STORAGE_PATH.value,STORAGE.HISTORY_FILE.value)):
        history = read_json_file(STORAGE.STORAGE_PATH.value,STORAGE.HISTORY_FILE.value)
        try:
            return history
        except Exception:
            return []
    return []


def get_currentdate_forentry():
    now = datetime.now()
    return f"{now.day:02d}/{now.month:02d}/{now.year}"

def now_greater_than_date(date_string):
    now = datetime.now()
    input_date = datetime.strptime(date_string, "%d/%m/%Y")
    return now > input_date