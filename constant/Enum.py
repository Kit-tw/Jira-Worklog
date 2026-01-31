from enum import Enum
import os 
# TODO : CREATE bash file for running os.path.join(os.environ["USERPROFILE"], "Documents" locate where file store and Markdown file for document
# TODO : add ICON tips and hover show storage location -> os.path.join(os.environ["USERPROFILE"], "Documents"
# create hover and show tip to https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class URL(Enum):
    def JIRA_POST_INSERT_WORKLOG_PATH(key :str) -> str :
        return f"/rest/api/3/issue/{key}/worklog"
    JIRA_GET_API_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
    JIRA_ISSUE_PATH = "/rest/api/3/issue/"
    SPREAD_SHEET_ID = "1gyU9eyHkcHGO5LdHW9kn6zXxUWR58ILg0-fX5WRbOlQ"
    SPREAD_SHEET_NAME = "Worklog Template"
class STORAGE(Enum):
    def GET_DOCUMENT_PATH() -> str:
        return  os.path.join(os.environ["USERPROFILE"], "Documents") 
    DIRECTORY_NAME = "Worklog"
    GOOGLE_API_CREDENTIALS_FILE = "credentials.json"
    GOOGLE_API_AUTHORIZED_USER_FILE = "authorized_user.json"
    TOKEN_FILE = "token.json"
    INFORMATION_FILE = "info.json"
    STORAGE_PATH = f"{GET_DOCUMENT_PATH()}/{DIRECTORY_NAME}"
    #TODO : SHOULD YOU REFACTOR COMMON UTIL to use only path?
    TOKEN_PATH = f"{STORAGE_PATH}/{TOKEN_FILE}"
    GOOGLE_API_CREDENTIALS_PATH = f"{STORAGE_PATH}/{GOOGLE_API_CREDENTIALS_FILE}"
    GOOGLE_API_AUTHORIZED_USER_PATH = f"{STORAGE_PATH}/{GOOGLE_API_AUTHORIZED_USER_FILE}"
    INFORMATION_PATH = f"{STORAGE_PATH}/{INFORMATION_FILE}"


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
    DATE = "\\d{2}\\/\\d{2}\\/\\d{4}" #pattern dd/mm/yyyy (0-9)
    HOUR_JIRA = "\\d+[Hh]" #pattern [0-9]+h
    MINUTE_JIRA = "\\d+[Mm]" #pattern [0-9]+h