import os
import json
import shutil
from typing import Any, Optional


def find(path: str, name: str) -> Optional[str]:
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_json(path: str, filename: str, data: Any) -> None:
    ensure_directory(path)
    with open(os.path.join(path, filename), 'w') as f:
        json.dump(data, f)


def delete_file(path: str, filename: str) -> None:
    full_path = os.path.join(path, filename)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"'{filename}' not found in {path}")
    os.remove(full_path)


def read_json(path: str, filename: str) -> Any:
    with open(os.path.join(path, filename), 'r') as f:
        return json.load(f)


def read_json_by_path(full_path: str) -> Any:
    with open(full_path, 'r') as f:
        return json.load(f)


def copy_file(src: str, dest: str) -> None:
    shutil.copyfile(src, dest)
