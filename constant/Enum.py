from enum import Enum
from pathlib import Path


def _storage_base() -> str:
    return str(Path.home() / "Documents")


def _project_root() -> str:
    return str(Path(__file__).parent.parent)


_WORKLOG_DIR = "Worklog"
_STORAGE = f"{_storage_base()}/{_WORKLOG_DIR}"
_ROOT = _project_root()


class URL(Enum):
    JIRA_GET_API_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
    GSPREAD_GOOGLE_API_DOC = "https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id"
    GOOGLE_DEVELOPER_CONSOLE = "https://console.cloud.google.com/apis/dashboard"
    JIRA_ISSUE_PATH = "/rest/api/3/issue/"
    SPREAD_SHEET_ID = "1gyU9eyHkcHGO5LdHW9kn6zXxUWR58ILg0-fX5WRbOlQ"
    SPREAD_SHEET_NAME = "Worklog Template"

    @staticmethod
    def jira_worklog_path(key: str) -> str:
        return f"/rest/api/3/issue/{key}/worklog"


class STORAGE(Enum):
    DIRECTORY_NAME = _WORKLOG_DIR
    IMAGE_DIRECTORY_NAME = "image"
    GOOGLE_API_CREDENTIALS_FILE = "credentials.json"
    GOOGLE_API_AUTHORIZED_USER_FILE = "authorized_user.json"
    TOKEN_FILE = "token.json"
    INFORMATION_FILE = "info.json"
    HISTORY_FILE = "history.json"
    GOOGLE_SHEET_IMAGE = "google_sheet_image.png"
    TOOLTIP_IMAGE = "tooltip_image.png"
    STORAGE_PATH = _STORAGE
    IMAGE_PATH = f"{_ROOT}/image"
    TOKEN_PATH = f"{_STORAGE}/token.json"
    GOOGLE_API_CREDENTIALS_PATH = f"{_STORAGE}/credentials.json"
    GOOGLE_API_AUTHORIZED_USER_PATH = f"{_STORAGE}/authorized_user.json"
    INFORMATION_PATH = f"{_STORAGE}/info.json"


class WIDGET(Enum):
    PAD_X = 50
    PAD_Y = 20
    WIDTH = 40
    HEIGHT = 40


class TEXTSIZE(Enum):
    TEXT_LG = 30
    TEXT_MD = 24
    TEXT_SM = 16
    TEXT_X_SM = 14


class REGEX(Enum):
    DATE = r"\d{2}\/\d{2}\/\d{4}"
    HOUR_JIRA = r"\d+[Hh]"
    MINUTE_JIRA = r"\d+[Mm]"
