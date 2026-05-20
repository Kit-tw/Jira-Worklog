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
            hours = divmod(time_in_s, 3600)[0]
            working_hours = 8 if hours > 8 else max(1, hours)
            
            obj = {
                "date" : f"{before_date.day:02d}/{before_date.month:02d}/{before_date.year}",
                "time_spend" : f"{int(working_hours)}h" ,
                "description" : message[-1]
            }
            return obj
        except Exception as e:
            raise Exception(f"Could not get git details: {str(e)}")