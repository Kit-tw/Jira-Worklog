import os
import json
import shutil


def find(path: str, name: str) -> str | None:
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None


def check_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_file(path: str, filename: str, data: object) -> str:
    check_directory(path)
    full_path = os.path.join(path, filename)
    with open(full_path, 'w') as f:
        json.dump(data, f)
    return full_path


def delete_file(path: str, filename: str) -> None:
    full_path = os.path.join(path, filename)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"file '{filename}' not found in {path}")
    os.remove(full_path)


def read_json_file(path: str, filename: str) -> any:
    full_path = os.path.join(path, filename)
    with open(full_path, 'r') as f:
        return json.load(f)


def read_json_file_by_full_path(full_path: str) -> any:
    with open(full_path, 'r') as f:
        return json.load(f)


def copy_file(src: str, dest: str) -> None:
    shutil.copyfile(src, dest)
