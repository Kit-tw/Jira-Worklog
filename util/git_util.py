import subprocess
import os 
from git import Repo
from util.gui_util import GuiUtil
from util.jira_util import JiraUtil
from datetime import datetime, timedelta
class GitUtil:
    def __init__(self):
        self.cur_dir = self.get_current_directory()
        self.gui_util = GuiUtil(self)
        self.jira_util = JiraUtil()
        

    # TODO : Add way to check if current_directory isn't git send Error
    def get_current_directory(self) -> str:
        return os.getcwd()
    
    def get_issueName(self) -> str :
        try:
            return Repo(self.cur_dir).active_branch.name
        except Exception as e:
            self.gui_util.show_dialog("Error", "cancel", "Current directory is not have .git", options="OK")

    def get_issue_key(self) -> str:
        return self.jira_util.fetch_issue(self.get_issueName())

    def get_git_detail(self):
        cur_log = Repo(self.cur_dir).active_branch.log()
        create_branch_date = datetime.fromtimestamp(cur_log[0].time[0])
        print(create_branch_date)
        message = []
        date_time = []
        for entry in cur_log:
            message.append(entry.message)
            date_time.append(datetime.fromtimestamp(entry.time[0]))
        time : timedelta = date_time[-1] - date_time[-2]
        time_in_s = time.total_seconds()
        hours = divmod(time_in_s, 3600)[0]
        #TODO : Clear messy code
        working_hours = 8 if hours > 8 else hours
        obj = {
            "date" : f"{date_time[-1].day}/{date_time[-1].month}/{date_time[-1].year}",
            "time_spend" : f"{int(working_hours)}h" ,
            "description" : message[-1]
        }
        return obj