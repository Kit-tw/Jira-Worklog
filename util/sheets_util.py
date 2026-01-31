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
        self.date = "14/01/2026"
        self.time = "1h 3m"
        self.desciprtion = "Testing"
        print("RunUtil")
        self.dt = datetime.strptime(self.date, "%d/%m/%Y")
        self.gc = self.authenticate()
        self.sheet_id = self.get_sheet_id()
        self.worksheet = self.gc.open_by_key(self.sheet_id)
        self.jira_issue_add()
        self.worklog_add()

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

    def jira_issue_add(self):
        jira_sheet =  self.worksheet.worksheet(self.jira_issue_sheetname)
        lastrow = int(jira_sheet.acell('V2').value) + 1
        jira_sheet.update_cell(lastrow,1,self.key)

    def jira_issue_get_summary(self):
        SUMMARY_DROPDOWN_COL = 5 # "E" Col
        jira_sheet = self.worksheet.worksheet(self.jira_issue_sheetname)
        issue = jira_sheet.find(self.key)
        return jira_sheet.cell(issue.row,SUMMARY_DROPDOWN_COL).value
    
    def jira_issue_get_worklog_link(self):
        WORKLOG_LINK_COL = 3 # "C" Col
        jira_sheet = self.worksheet.worksheet(self.jira_issue_sheetname)
        issue = jira_sheet.find(self.key)
        return jira_sheet.cell(issue.row,WORKLOG_LINK_COL).value

    def worklog_add(self):
        worklog_sheet = self.worklog_get_sheet()
        date_cell_pattern = f"{self.dt.year}-{self.dt.month:02d}-{self.dt.day:02d}"
        print(date_cell_pattern)
        find_cell =  worklog_sheet.findall(date_cell_pattern)
        empty_comment_row = None

        for cell in find_cell:
            comment_cell = worklog_sheet.cell(cell.row,4)
            print(f"Loop {comment_cell.address} : {comment_cell.value}")
            if(comment_cell.value is None):
                empty_comment_row = comment_cell.row
                break

        if(empty_comment_row is None):
            print("Can't Find")
            src_row = find_cell[-1].row
            dest_row = find_cell[-1].row + 1
            empty_comment_row = dest_row
            print(f"src_row : {src_row} dest_row = {dest_row}")
            self.worklog_sheet_new_row(worklog_sheet,src_row,dest_row)

        print(f"Empty : {empty_comment_row}")
        self.worklog_insert_cell(worklog_sheet,empty_comment_row)

    def worklog_insert_cell(self,
                            worksheet : gspread.Worksheet,
                            row : str):
        SUMMARY_DROPDOWN_COL = 4 #"D" col
        COMMENT_COL = 5 #"E" col
        HOUR_COL = 6 #"F" col
        MINUTE_COL = 7 #"G" col
        REMARK_COL = 11 #"K" col
        OPTION_COL = 12 #"L" col
        WORKLOG_LINK_COL = 13 #"M" col
        summary_value = self.jira_issue_get_summary()
        description_value = self.desciprtion
        hour_value = 1
        minute_value = 0
        remark_value = "Success"
        option_value = "Add"
        worklog_link_value = self.jira_issue_get_worklog_link()
        worksheet.update_cell(row,SUMMARY_DROPDOWN_COL,summary_value)
        worksheet.update_cell(row,COMMENT_COL,description_value)
        worksheet.update_cell(row,HOUR_COL,hour_value)
        worksheet.update_cell(row,MINUTE_COL,minute_value)
        worksheet.update_cell(row,REMARK_COL,remark_value)
        worksheet.update_cell(row,OPTION_COL,option_value)
        worksheet.update_cell(row,WORKLOG_LINK_COL,worklog_link_value)


        

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


    def worklog_get_sheet(self) -> gspread.Worksheet:
        worklog_sheetname = self.worklog_get_sheetname()
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
    
    def worklog_get_sheetname(self) -> str:
        return f"{self.dt.year}/{self.dt.month:02d}"


