import gspread
import util.common_util as common_util
from util.gui_util import GuiUtil
from constant.Enum import (STORAGE,URL)
#TODO : ADD HANDLE ERROR
class SheetsUtil:
    def __init__(self):
        self.home_sheetname = "Home"
        self.template_sheetname = "Template"
        self.jira_issue_sheetname = "jira-issue"
        self.gc = self.authenticate()
        self.sheet_id = self.get_sheet_id()
        self.worksheet = self.gc.open_by_key(self.sheet_id)
        self.test = self.add_jira_issue()

    def authenticate(self):
        credentials_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_CREDENTIALS_FILE.value}"
        authorized_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_AUTHORIZED_USER_FILE.value}"
        return gspread.oauth(
            credentials_filename=credentials_path,
            authorized_user_filename=authorized_path
        )
    
    def get_sheet_id(self):
        if(not common_util.find(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value)):
            dialog = GuiUtil().show_dialog("Error", "cancel", f"You Do not have spreadsheets template", option_1="Add", option_2="OK")
            if(dialog.get() == "Add"):
                return self.copy_sheets()
        info = common_util.read_json_file(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value)
        return info["spreadsheetId"]

    def copy_sheets(self):
        new_spreadsheet = self.gc.copy(URL.SPREAD_SHEET_ID.value,title=URL.SPREAD_SHEET_NAME.value)
        print(new_spreadsheet.id)
        data = {"spreadsheetId" : new_spreadsheet.id}
        common_util.save_file(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value,data)
        return new_spreadsheet.id

    def add_jira_issue(self):
        jira_sheet =  self.worksheet.worksheet(self.jira_issue_sheetname)
        lastest_cell = jira_sheet.row_count
        print(lastest_cell)

    def get_last_row(self,sheetname):
        lastrow = 2
        
