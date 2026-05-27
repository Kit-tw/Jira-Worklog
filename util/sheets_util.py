import os
import re
import gspread
from datetime import datetime
from google.auth.exceptions import RefreshError

import util.file_util as file_util
from constant.Enum import STORAGE, URL, REGEX


class SheetsUtil:
    HOME_SHEETNAME = "Home"
    TEMPLATE_SHEETNAME = "Template"
    JIRA_ISSUE_SHEETNAME = "jira-issue"

    def __init__(self):
        try:
            self.gc = self._authenticate()
        except RefreshError:
            self.gc = self._authenticate(force_reauth=True)
        sheet_id = self._get_sheet_id()
        self.worksheet = self.gc.open_by_key(sheet_id)

    def insert(self, key: str, date: str, time: str, description: str) -> None:
        dt = datetime.strptime(date, "%d/%m/%Y")
        self._jira_issue_add(key)
        self._worklog_add(key, dt, time, description)

    def copy_template(self) -> str:
        new_spreadsheet = self.gc.copy(URL.SPREAD_SHEET_ID.value, title=URL.SPREAD_SHEET_NAME.value)
        file_util.save_json(
            STORAGE.STORAGE_PATH.value,
            STORAGE.INFORMATION_FILE.value,
            {"spreadsheetId": new_spreadsheet.id},
        )
        return new_spreadsheet.id

    def _authenticate(self, force_reauth: bool = False) -> gspread.Client:
        credentials_path = STORAGE.GOOGLE_API_CREDENTIALS_PATH.value
        authorized_path = STORAGE.GOOGLE_API_AUTHORIZED_USER_PATH.value
        if force_reauth and os.path.exists(authorized_path):
            os.remove(authorized_path)
        return gspread.oauth(
            credentials_filename=credentials_path,
            authorized_user_filename=authorized_path,
        )

    def _get_sheet_id(self) -> str:
        if not file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.INFORMATION_FILE.value):
            raise Exception("No spreadsheet configured. Please add a spreadsheet template.")
        info = file_util.read_json(STORAGE.STORAGE_PATH.value, STORAGE.INFORMATION_FILE.value)
        return info["spreadsheetId"]

    def _jira_issue_add(self, key: str) -> None:
        jira_sheet = self.worksheet.worksheet(self.JIRA_ISSUE_SHEETNAME)
        last_row = int(jira_sheet.acell('V2').value) + 1
        jira_sheet.update_cell(last_row, 1, key)

    def _jira_issue_get_summary(self, key: str) -> str:
        SUMMARY_COL = 5
        jira_sheet = self.worksheet.worksheet(self.JIRA_ISSUE_SHEETNAME)
        issue = jira_sheet.find(key)
        return jira_sheet.cell(issue.row, SUMMARY_COL).value

    def _jira_issue_get_worklog_link(self, key: str) -> str:
        WORKLOG_LINK_COL = 3
        jira_sheet = self.worksheet.worksheet(self.JIRA_ISSUE_SHEETNAME)
        issue = jira_sheet.find(key)
        return jira_sheet.cell(issue.row, WORKLOG_LINK_COL).value

    def _worklog_add(self, key: str, dt: datetime, time: str, description: str) -> None:
        worklog_sheet = self._get_or_create_worklog_sheet(dt)
        row = self._find_empty_row(worklog_sheet, dt)
        self._insert_cells(worklog_sheet, row, key, time, description)

    def _find_empty_row(self, worksheet: gspread.Worksheet, dt: datetime) -> int:
        date_pattern = f"{dt.year}-{dt.month:02d}-{dt.day:02d}"
        cells = worksheet.findall(date_pattern)
        for cell in cells:
            comment_cell = worksheet.cell(cell.row, 4)
            if comment_cell.value is None:
                return comment_cell.row
        src_row = cells[-1].row
        dest_row = src_row + 1
        self._duplicate_row(worksheet, src_row, dest_row)
        return dest_row

    def _insert_cells(self, worksheet: gspread.Worksheet, row: int, key: str, time: str, description: str) -> None:
        COL = {"summary": 4, "comment": 5, "hour": 6, "minute": 7, "remark": 11, "option": 12, "worklog_link": 13}
        values = {
            COL["summary"]: self._jira_issue_get_summary(key),
            COL["comment"]: description,
            COL["hour"]: self._parse_time_part(time, REGEX.HOUR_JIRA.value, "h"),
            COL["minute"]: self._parse_time_part(time, REGEX.MINUTE_JIRA.value, "m"),
            COL["remark"]: "Success",
            COL["option"]: "Add",
            COL["worklog_link"]: self._jira_issue_get_worklog_link(key),
        }
        worksheet.batch_update([
            {"range": gspread.utils.rowcol_to_a1(row, col), "values": [[val]]}
            for col, val in values.items()
        ])

    def _parse_time_part(self, time: str, regex: str, replace: str) -> str:
        try:
            return re.search(regex, time).group(0).replace(replace, "")
        except Exception:
            return ""

    def _get_or_create_worklog_sheet(self, dt: datetime) -> gspread.Worksheet:
        sheet_name = f"{dt.year}/{dt.month:02d}"
        try:
            return self.worksheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            template = self.worksheet.worksheet(self.TEMPLATE_SHEETNAME)
            self.worksheet.duplicate_sheet(source_sheet_id=template.id, new_sheet_name=sheet_name)
            ws = self.worksheet.worksheet(sheet_name)
            ws.update_acell("Q3", f"{dt.month:02d}")
            ws.update_acell("Q4", dt.year)
            return ws

    def _duplicate_row(self, worksheet: gspread.Worksheet, src_row: int, dest_row: int) -> None:
        TEMPLATE_RANGE = "A:N"
        CLEAR_COLUMNS = ["D:G", "K", "M"]
        worksheet.copy_range(
            source=f"{TEMPLATE_RANGE}{src_row}",
            dest=f"{TEMPLATE_RANGE}{dest_row}",
        )
        worksheet.batch_clear([f"{col}{dest_row}" for col in CLEAR_COLUMNS])
