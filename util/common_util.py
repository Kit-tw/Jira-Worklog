import os
import webbrowser
from datetime import datetime, timezone
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

import util.file_util as file_util
from constant.Enum import STORAGE


def find(path: str, name: str) -> Optional[str]:
    return file_util.find(path, name)


def open_url(url: str) -> None:
    webbrowser.open(url)


def date_str_to_iso(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"


def get_currentdate_forentry() -> str:
    now = datetime.now()
    return f"{now.day:02d}/{now.month:02d}/{now.year}"


def now_greater_than_date(date_string: str, fmt: str) -> bool:
    return datetime.now() > datetime.strptime(date_string, fmt)


def get_user(email: str, api: str, prefix: str) -> requests.Response:
    url = f"https://{prefix}.atlassian.net/rest/api/3/myself"
    return requests.get(url, headers={"Accept": "application/json"}, auth=HTTPBasicAuth(email, api))


def get_worklog_history() -> list:
    if file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value):
        try:
            return file_util.read_json(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
        except Exception:
            return []
    return []


def get_min_time_spend() -> int:
    try:
        info_path = os.path.join(STORAGE.STORAGE_PATH.value, STORAGE.INFORMATION_FILE.value)
        if os.path.exists(info_path):
            data = file_util.read_json_by_path(info_path)
            return int(data.get("min_time_spend", 15))
    except Exception:
        pass
    return 15
