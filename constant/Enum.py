from enum import Enum

class URL(Enum):
    JIRA_GET_API_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
    JIRA_ISSUE_PATH = "/rest/api/3/issue/"

class STORAGE(Enum):
    GOOGLE_API_CREDENTIALS_FILE = "credentials.json"
    GOOGLE_API_AUTHORIZED_USER_FILE = "authorized_user.json"
    TOKEN_FILE = "token.json"
    FILE_PATH = "."
    STORAGE_PATH ="."


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