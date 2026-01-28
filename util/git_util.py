import subprocess
import os 
from git import Repo
from util.gui_util import GuiUtil
from util.jira_util import JiraUtil
from datetime import datetime
class GitUtil:
    def __init__(self):
        self.cur_dir = self.get_current_directory()
        self.gui_util = GuiUtil()
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

    # TODO : implement return step to extract 5 lastest commit worklog
    # TODO : add check for maximum hour checkbox from worklog_page
    def get_git_detail(self):
        cur_log = Repo(self.cur_dir).active_branch.log()
        create_branch_date = datetime.fromtimestamp(cur_log[0].time[0])
        print(create_branch_date)
        for entry in cur_log:
            message = entry.message
            date_time = datetime.fromtimestamp(entry.time[0])
            print(f"{message}   {date_time}" )
        return