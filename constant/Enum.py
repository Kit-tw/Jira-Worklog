from enum import Enum
import os 
# TODO : CREATE bash file for running os.path.join(os.environ["USERPROFILE"], "Documents" locate where file store and Markdown file for document
class URL(Enum):
    JIRA_GET_API_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
    JIRA_ISSUE_PATH = "/rest/api/3/issue/"
    def JIRA_POST_INSERT_WORKLOG_PATH(key :str) -> str :
        return f"/rest/api/3/issue/{key}/worklog"

class STORAGE(Enum):
    def GET_DOCUMENT_PATH() -> str:
        return  os.path.join(os.environ["USERPROFILE"], "Documents") 
    GOOGLE_API_CREDENTIALS_FILE = "credentials.json"
    GOOGLE_API_AUTHORIZED_USER_FILE = "authorized_user.json"
    TOKEN_FILE = "token.json"
    DIRECTORY_NAME = "Worklog"
    STORAGE_PATH = GET_DOCUMENT_PATH() + "/" + DIRECTORY_NAME


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