import os
import webbrowser
import json
import shutil
import util.file_util as file_util
from util.gui_util import GuiUtil
from datetime import datetime, timezone
import requests
from requests.auth import HTTPBasicAuth
from constant.Enum import STORAGE


def find(path: str, name: str):
    return file_util.find(path, name)


def check_directory(path: str):
    file_util.check_directory(path)


def open_url(url):
    webbrowser.open(url)


def save_file(path: str, file: str, data: object, showDialog: bool = True) -> None:
    try:
        full_path = file_util.save_file(path, file, data)
        if showDialog:
            GuiUtil().show_dialog("Success", "check", f"file has been saved at {full_path}", options="OK")
    except Exception as e:
        print(e)
        GuiUtil().show_dialog("Error", "cancel", "Failed to save file", options="OK")


def delete_file(path: str, file: str, showDialog: bool = True) -> None:
    try:
        file_util.delete_file(path, file)
        if showDialog:
            GuiUtil().show_dialog("Success", "check", f"file '{file}' has been deleted from {path}", options="OK")
    except FileNotFoundError as e:
        GuiUtil().show_dialog("Error", "cancel", str(e), options="OK")
    except Exception as e:
        print(e)
        GuiUtil().show_dialog("Error", "cancel", "Failed to delete file", options="OK")


def read_json_file(path: str, filename: str) -> any:
    try:
        return file_util.read_json_file(path, filename)
    except Exception:
        GuiUtil().show_dialog("Error", "cancel", "Failed to read file", options="OK")
        return None


def read_json_file_by_full_path(full_path: str) -> any:
    try:
        return file_util.read_json_file_by_full_path(full_path)
    except Exception:
        GuiUtil().show_dialog("Error", "cancel", "Failed to read file", options="OK")
        return None


def copy_file(src: str, dest: str):
    try:
        file_util.copy_file(src, dest)
        GuiUtil().show_dialog("Success", "check", f"successfully copied to '{dest}'", options="OK")
    except shutil.SameFileError:
        GuiUtil().show_dialog("Error", "cancel", "Source and destination represent the same file.", options="OK")
    except PermissionError:
        GuiUtil().show_dialog("Error", "cancel", "Permission denied.", options="OK")
    except FileNotFoundError:
        GuiUtil().show_dialog("Error", "cancel", "Source file not found.", options="OK")
    except Exception as e:
        GuiUtil().show_dialog("Error", "cancel", f"An error occurred: {e}", options="OK")


def date_str_to_iso(date_str) -> str:
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"


def get_user(email, api, prefix):
    url = f"https://{prefix}.atlassian.net/rest/api/3/myself"
    auth = HTTPBasicAuth(email, api)
    headers = {"Accept": "application/json"}
    return requests.request("GET", url, headers=headers, auth=auth)


def get_worklog_history():
    if file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value):
        try:
            return file_util.read_json_file(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
        except Exception:
            return []
    return []


def get_currentdate_forentry():
    now = datetime.now()
    return f"{now.day:02d}/{now.month:02d}/{now.year}"


def now_greater_than_date(date_string, format):
    now = datetime.now()
    input_date = datetime.strptime(date_string, format)
    return now > input_date


def get_min_time_spend() -> int:
    try:
        info_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.INFORMATION_FILE.value)
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                data = json.load(f)
                return int(data.get("min_time_spend", 15))
    except Exception:
        pass
    return 15
