import gspread
from datetime import datetime
import util.common_util as common_util
from util.gui_util import GuiUtil
from constant.Enum import (STORAGE,URL)
#TODO : ADD HANDLE ERROR
class SheetsUtil:
    def __init__(self,
                 key : str,
                 date : str,
                 time : str,
                 description : str):
        self.home_sheetname = "Home"
        self.template_sheetname = "Template"
        self.jira_issue_sheetname = "jira-issue"
        self.key = "WFW-100"
        self.date = "13/01/2026"
        self.time = "1h 3m"
        self.desciprtion = "Testing"
        print("RunUtil")
        self.dt = datetime.strptime(self.date, "%d/%m/%Y")
        self.gc = self.authenticate()
        self.sheet_id = self.get_sheet_id()
        self.worksheet = self.gc.open_by_key(self.sheet_id)
        self.add_jira_issue()
        self.add_worklog()

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
        lastrow = int(jira_sheet.acell('V2').value) + 1
        jira_sheet.update_cell(lastrow,1,self.key)

    def add_worklog(self):
        worklog_sheet = self.get_worklog_sheet()
        date_cell_pattern = f"{self.dt.year}-{self.dt.month:02d}-{self.dt.day:02d}"
        print(date_cell_pattern)
        find_cell =  worklog_sheet.findall(date_cell_pattern)
        print(find_cell)
        

    def get_worklog_sheet(self) -> gspread.Worksheet:
        worklog_sheetname = self.get_worklog_sheetname()
        try:
            worksheet = self.worksheet.worksheet(worklog_sheetname)
        except gspread.exceptions.WorksheetNotFound:
            #TODO: Dialog asking for Dupe? or Unnessary
            print("not Found")
            template_sheet = self.worksheet.worksheet(self.template_sheetname)
            self.worksheet.duplicate_sheet(
            source_sheet_id=template_sheet.id,
            new_sheet_name=worklog_sheetname)

            worksheet =  self.worksheet.worksheet(worklog_sheetname)
            worksheet.update_acell("Q3",f"{self.dt.month:02d}")
            worksheet.update_acell("Q4",self.dt.year)
            print("Successfully Dupe")
        return worksheet
    
    def get_worklog_sheetname(self) -> str:
        return f"{self.dt.year}/{self.dt.month:02d}"


