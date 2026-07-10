"""
Business logic for submitting a worklog entry.
No dependency on any GUI framework or CLI I/O — raises exceptions on failure.
"""
import os
import re
import util.file_util as file_util
import util.common_util as common_util
from dataclasses import dataclass
from constant.Enum import STORAGE, REGEX


@dataclass
class WorklogRequest:
    issue_key: str
    time_spend: str
    date: str           # dd/mm/yyyy
    description: str | None = None


@dataclass
class WorklogResult:
    issue_key: str
    issue_name: str
    date: str
    time_spend: str
    description: str | None


class WorklogService:
    def __init__(self, jira_util=None):
        if jira_util is None:
            from util.jira_util import JiraUtil
            jira_util = JiraUtil()
        self._jira = jira_util

    async def submit(self, request: WorklogRequest) -> WorklogResult:
        self._validate(request)
        date_iso = common_util.date_str_to_iso(request.date)
        issue_name = await self._jira.fetch_issue(request.issue_key)
        status, response_text = await self._jira.post_insert_worklog(
            request.issue_key,
            request.time_spend,
            date_iso,
            request.description,
        )
        if not (200 <= status < 300):
            raise Exception(f"Jira API error (status {status}): {response_text}")
        self._save_history(request.issue_key, issue_name)
        return WorklogResult(
            issue_key=request.issue_key,
            issue_name=issue_name,
            date=request.date,
            time_spend=request.time_spend,
            description=request.description,
        )

    def submit_to_sheets(self, result: WorklogResult) -> None:
        credentials_path = os.path.join(
            STORAGE.STORAGE_PATH.value, STORAGE.GOOGLE_API_CREDENTIALS_FILE.value
        )
        if not os.path.exists(credentials_path):
            raise FileNotFoundError("Google API credentials not found.")
        from util.sheets_util import SheetsUtil
        SheetsUtil(
            key=result.issue_key,
            date=result.date,
            time=result.time_spend,
            description=result.description or "",
        )

    def _validate(self, request: WorklogRequest) -> None:
        if not request.issue_key or not request.issue_key.strip():
            raise ValueError("Issue key is required.")
        if not request.time_spend:
            raise ValueError("Time spent is required.")
        if not re.match(REGEX.DATE.value, request.date):
            raise ValueError("Date must be in dd/mm/yyyy format.")

    def _save_history(self, issue_key: str, issue_name: str) -> None:
        history = common_util.get_worklog_history()
        if any(item.get("key") == issue_key for item in history):
            return
        history.append({
            "key": issue_key,
            "name": issue_name,
            "summary": f"{issue_key} : {issue_name}",
        })
        try:
            file_util.save_file(
                STORAGE.STORAGE_PATH.value,
                STORAGE.HISTORY_FILE.value,
                history,
            )
        except Exception as e:
            print(f"Warning: Failed to update history: {e}")
