import gspread
from datetime import datetime
import util.common_util as common_util
from util.jira_util import JiraUtil
from constant.Enum import (STORAGE,URL,REGEX)
import re
import os
from google.auth.exceptions import RefreshError
class SheetsUtil:
    def __init__(self,
                 key : str,
                 date : str,
                 time : str,
                 description : str):
        self.HOME_SHEETNAME = "Home"
        self.TEMPLATE_SHEETNAME = "Template"
        self.JIRA_ISSUE_SHEETNAME = "jira-issue"
        self.key = key
        self.date = date
        self.time = time
        self.description = description
        self.dt = datetime.strptime(self.date, "%d/%m/%Y")
        try:
            self.gc = self.authenticate()
            self.sheet_id = self.get_sheet_id()
            self.worksheet = self.gc.open_by_key(self.sheet_id)
        except RefreshError:
            self.gc = self.authenticate(force_reauth=True)
            self.sheet_id = self.get_sheet_id()
            self.worksheet = self.gc.open_by_key(self.sheet_id)
            
        self.jira_issue_add()
        self.worklog_add()

    def authenticate(self, force_reauth=False):
        credentials_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_CREDENTIALS_FILE.value}"
        authorized_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_AUTHORIZED_USER_FILE.value}"
        
        if force_reauth and os.path.exists(authorized_path):
            os.remove(authorized_path)
        return gspread.oauth(
            credentials_filename=credentials_path,
            authorized_user_filename=authorized_path
        )
    
    def get_sheet_id(self):
        if(not common_util.find(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value)):
            raise Exception("You do not have a spreadsheets template. Please add one.")
        info = common_util.read_json_file(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value)
        return info["spreadsheetId"]

    def copy_sheets(self):
        new_spreadsheet = self.gc.copy(URL.SPREAD_SHEET_ID.value,title=URL.SPREAD_SHEET_NAME.value)
        data = {"spreadsheetId" : new_spreadsheet.id}
        common_util.save_file(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value,data)
        self.home_add()
        return new_spreadsheet.id

    def home_add(self):
        home_worksheet = self.worksheet.worksheet(self.HOME_SHEETNAME)
        jira_util = JiraUtil() 
        ROW = {
            "email": 3, # D
            "api_token": 4, # E
            "jira_site": 5, # F
        }

        # Build values
        values = {
            ROW["email"]: jira_util.mail,
            ROW["api_token"]: jira_util.api_token,
            ROW["jira_site"]: jira_util.full_url
        }
        home_worksheet.batch_update([
            {
                "range": f"{gspread.utils.rowcol_to_a1(row, 2)}",
                "values": [[value]],
            }
            for row, value in values.items()
        ])


    def jira_issue_add(self):
        jira_sheet =  self.worksheet.worksheet(self.JIRA_ISSUE_SHEETNAME)
        lastrow = int(jira_sheet.acell('V2').value) + 1
        jira_sheet.update_cell(lastrow,1,self.key)

    def jira_issue_get_summary(self):
        SUMMARY_DROPDOWN_COL = 5 # "E" Col
        jira_sheet = self.worksheet.worksheet(self.JIRA_ISSUE_SHEETNAME)
        issue = jira_sheet.find(self.key)
        return jira_sheet.cell(issue.row,SUMMARY_DROPDOWN_COL).value
    
    def jira_issue_get_worklog_link(self):
        WORKLOG_LINK_COL = 3 # "C" Col
        jira_sheet = self.worksheet.worksheet(self.JIRA_ISSUE_SHEETNAME)
        issue = jira_sheet.find(self.key)
        return jira_sheet.cell(issue.row,WORKLOG_LINK_COL).value

    def worklog_add(self):
        worklog_sheet = self.worklog_get_sheet()
        empty_comment_row = self.worklog_find_empty_row(worklog_sheet)
        self.worklog_insert_cell(worklog_sheet,empty_comment_row)

    def worklog_find_empty_row(self,
                               worksheet: gspread.Worksheet):
        date_cell_pattern = f"{self.dt.year}-{self.dt.month:02d}-{self.dt.day:02d}"
        find_cell =  worksheet.findall(date_cell_pattern)
        for cell in find_cell:
            comment_cell = worksheet.cell(cell.row,4)
            print(f"Loop {comment_cell.address} : {comment_cell.value}")
            if(comment_cell.value is None):
                return comment_cell.row

        print("debug: All Row have been inserted, Duplicate Row.")
        src_row = find_cell[-1].row
        dest_row = find_cell[-1].row + 1
        self.worklog_sheet_new_row(worksheet,src_row,dest_row)
        return dest_row

    def worklog_insert_cell(
        self,
        worksheet: gspread.Worksheet,
        row: int,
    ):
        # Column indices (1-based)
        COL = {
            "summary": 4,      # D
            "comment": 5,      # E
            "hour": 6,         # F
            "minute": 7,       # G
            "remark": 11,      # K
            "option": 12,      # L
            "worklog_link": 13 # M
        }

        # Build values
        values = {
            COL["summary"]: self.jira_issue_get_summary(),
            COL["comment"]: self.description,
            COL["hour"]: self.get_hourOrMinute_value(REGEX.HOUR_JIRA.value,"h"),
            COL["minute"]: self.get_hourOrMinute_value(REGEX.MINUTE_JIRA.value,"m"),
            COL["remark"]: "Success",
            COL["option"]: "Add",
            COL["worklog_link"]: self.jira_issue_get_worklog_link(),
        }

        worksheet.batch_update([
            {
                "range": f"{gspread.utils.rowcol_to_a1(row, col)}",
                "values": [[value]],
            }
            for col, value in values.items()
        ])
        print(f"debug: Successfully insert worklog at Row : {row}")

    def get_hourOrMinute_value(self,regex,replace):
        try:
            return re.search(regex, self.time).group(0).replace(replace, "")
        except Exception:
            return ""
        

    def worklog_sheet_new_row(self,
                              worksheet : gspread.Worksheet,
                              src_row : str,
                              dest_row : str):
            TEMPLATE_RANGE = "A:N"
            CLEAR_COLUMNS = ["D:G", "K", "M"]
            # Copy format
            worksheet.copy_range(
                source=f"{TEMPLATE_RANGE}{src_row}",
                dest=f"{TEMPLATE_RANGE}{dest_row}",
                )
            # Clear user-input columns
            worksheet.batch_clear([
                f"{col}{dest_row}" for col in CLEAR_COLUMNS
            ])
            print("debug: Successfully Duplicate row")


    def worklog_get_sheet(self) -> gspread.Worksheet:
        worklog_sheetname = self.worklog_get_sheetname()
        try:
            worksheet = self.worksheet.worksheet(worklog_sheetname)
        except gspread.exceptions.WorksheetNotFound:
            print("debug: sheet not Found")
            template_sheet = self.worksheet.worksheet(self.TEMPLATE_SHEETNAME)
            self.worksheet.duplicate_sheet(
            source_sheet_id=template_sheet.id,
            new_sheet_name=worklog_sheetname)

            worksheet =  self.worksheet.worksheet(worklog_sheetname)
            worksheet.update_acell("Q3",f"{self.dt.month:02d}")
            worksheet.update_acell("Q4",self.dt.year)
            print("debug: Successfully Duplicate sheet")
        return worksheet
    
    def worklog_get_sheetname(self) -> str:
        return f"{self.dt.year}/{self.dt.month:02d}"


