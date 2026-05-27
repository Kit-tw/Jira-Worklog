import os
import re
from datetime import datetime
from git import Repo


class GitUtil:
    def __init__(self, directory: str = None):
        self.cur_dir = directory or os.getcwd()

    def get_issueName(self) -> str:
        try:
            branch_name = Repo(self.cur_dir).active_branch.name
            match = re.search(r'([A-Za-z][A-Za-z0-9]+-[0-9]+)', branch_name)
            if match:
                return match.group(1).upper()
            return branch_name
        except Exception:
            raise Exception("Current directory does not have a valid .git repository.")

    def get_git_detail(self) -> dict:
        try:
            cur_log = list(Repo(self.cur_dir).active_branch.log())
            if len(cur_log) < 2:
                raise Exception("Not enough commits to calculate time spent.")

            date_time = [datetime.fromtimestamp(entry.time[0]) for entry in cur_log]
            before_date = date_time[-1]
            current_date = date_time[-2]

            total_minutes = max(int((before_date - current_date).total_seconds() // 60), 1)
            hours = total_minutes // 60
            minutes = total_minutes % 60

            if hours >= 8:
                time_spend_str = "8h"
                total_minutes = 480
            else:
                parts = []
                if hours > 0:
                    parts.append(f"{hours}h")
                if minutes > 0:
                    parts.append(f"{minutes}m")
                time_spend_str = " ".join(parts)

            return {
                "date": f"{before_date.day:02d}/{before_date.month:02d}/{before_date.year}",
                "time_spend": time_spend_str,
                "time_spend_minutes": total_minutes,
                "description": cur_log[-1].message,
            }
        except Exception as e:
            raise Exception(f"Could not get git details: {str(e)}")
