import os 
import re
from git import Repo
from util.jira_util import JiraUtil
from datetime import datetime, timedelta

class GitUtil:
    def __init__(self):
        self.cur_dir = self.get_current_directory()
        self.jira_util = JiraUtil()

    def get_current_directory(self) -> str:
        return os.getcwd()
    
    def get_issueName(self) -> str :
        try:
            branch_name = Repo(self.cur_dir).active_branch.name
            match = re.search(r'([A-Za-z][A-Za-z0-9]+-[0-9]+)', branch_name)
            if match:
                return match.group(1).upper()
            return branch_name
        except Exception as e:
            raise Exception("Current directory does not have a valid .git repository.")

    async def get_issue_key(self) -> str:
        return await self.jira_util.fetch_issue(self.get_issueName())

    def get_git_detail(self):
        try:
            cur_log = list(Repo(self.cur_dir).active_branch.log())
            if len(cur_log) < 2:
                # Need at least two commits to compute time differential
                raise Exception("Not enough commits to calculate time spent.")

            message = [entry.message for entry in cur_log]
            date_time = [datetime.fromtimestamp(entry.time[0]) for entry in cur_log]

            before_date = date_time[-1]
            current_date = date_time[-2]

            time_spent = before_date - current_date
            time_in_s = time_spent.total_seconds()

            total_minutes = int(time_in_s // 60)
            if total_minutes <= 0:
                total_minutes = 1

            hours = total_minutes // 60
            minutes = total_minutes % 60

            if hours >= 8:
                time_spend_str = "8h"
            else:
                parts = []
                if hours > 0:
                    parts.append(f"{hours}h")
                if minutes > 0:
                    parts.append(f"{minutes}m")
                time_spend_str = " ".join(parts)

            obj = {
                "date" : f"{before_date.day:02d}/{before_date.month:02d}/{before_date.year}",
                "time_spend" : time_spend_str,
                "time_spend_minutes" : 480 if hours >= 8 else total_minutes,
                "description" : message[-1]
            }
            return obj
        except Exception as e:
            raise Exception(f"Could not get git details: {str(e)}")

    def get_reflog_entries(self) -> list:
        """Returns all branch reflog entries as a list, oldest first, newest last."""
        try:
            cur_log = list(Repo(self.cur_dir).active_branch.log())
            if not cur_log:
                return []
            entries = []
            for entry in cur_log:
                dt = datetime.fromtimestamp(entry.time[0])
                entries.append({
                    "datetime": dt,
                    "date": f"{dt.day:02d}/{dt.month:02d}/{dt.year}",
                    "time_str": f"{dt.hour:02d}:{dt.minute:02d}",
                    "message": entry.message.strip(),
                })
            return entries
        except Exception as e:
            raise Exception(f"Could not read reflog: {str(e)}")

    @staticmethod
    def clean_reflog_message(message: str) -> str:
        """Strip git reflog action prefixes, leaving the human-written part."""
        msg = message.strip()
        if re.match(r'^commit \(amend\): ', msg):
            return re.sub(r'^commit \(amend\): ', '', msg)
        if re.match(r'^commit: ', msg):
            return re.sub(r'^commit: ', '', msg)
        m = re.match(r'^merge ([^:]+):', msg, re.IGNORECASE)
        if m:
            return f"{m.group(1).strip()} (from merge)"
        return msg

    def calc_range_entries(self, entries: list, anchor_idx: int, end_idx: int) -> list:
        """
        Compute time and data for commits from anchor (exclusive) to end (inclusive).
        entries is oldest-first; anchor_idx < end_idx.
        """
        result = []
        for i in range(anchor_idx + 1, end_idx + 1):
            dt_current = entries[i]["datetime"]
            dt_prev = entries[i - 1]["datetime"]
            total_seconds = (dt_current - dt_prev).total_seconds()
            total_minutes = max(1, int(total_seconds // 60))
            hours = total_minutes // 60
            minutes = total_minutes % 60
            capped = hours >= 8
            if capped:
                time_str = "8h"
                time_minutes = 480
            else:
                parts = []
                if hours > 0:
                    parts.append(f"{hours}h")
                if minutes > 0:
                    parts.append(f"{minutes}m")
                time_str = " ".join(parts) if parts else "1m"
                time_minutes = total_minutes
            result.append({
                "date": entries[i]["date"],
                "time_spend": time_str,
                "time_spend_minutes": time_minutes,
                "description": entries[i]["message"],
                "raw_minutes": total_minutes,
                "capped": capped,
            })
        return result