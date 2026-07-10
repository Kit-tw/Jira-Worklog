import os
import pytest
from util.file_util import save_file, read_json_file, delete_file, find, copy_file


def test_save_and_read_json(tmp_path):
    data = {"key": "PROJ-1", "name": "Test Issue"}
    save_file(str(tmp_path), "test.json", data)
    result = read_json_file(str(tmp_path), "test.json")
    assert result == data


def test_save_creates_nested_directory(tmp_path):
    nested = str(tmp_path / "new_dir")
    save_file(nested, "x.json", {"a": 1})
    assert os.path.isfile(os.path.join(nested, "x.json"))


def test_save_returns_full_path(tmp_path):
    full_path = save_file(str(tmp_path), "out.json", {})
    assert full_path.endswith("out.json")
    assert os.path.isfile(full_path)


def test_delete_existing_file(tmp_path):
    (tmp_path / "del.json").write_text('{}')
    delete_file(str(tmp_path), "del.json")
    assert not (tmp_path / "del.json").exists()


def test_delete_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        delete_file(str(tmp_path), "missing.json")


def test_find_returns_path(tmp_path):
    (tmp_path / "token.json").write_text('{}')
    result = find(str(tmp_path), "token.json")
    assert result is not None
    assert result.endswith("token.json")


def test_find_returns_none_for_missing(tmp_path):
    assert find(str(tmp_path), "nope.json") is None


def test_copy_file(tmp_path):
    src = tmp_path / "src.json"
    src.write_text('{"x":1}')
    dest = str(tmp_path / "dest.json")
    copy_file(str(src), dest)
    assert os.path.isfile(dest)
    assert open(dest).read() == '{"x":1}'
