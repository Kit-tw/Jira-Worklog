import subprocess
import os 
from git import Repo
from util.gui_util import GuiUtil
from datetime import datetime
class GitUtil:
    def __init__(self):
        self.cur_dir = self.get_current_directory()
        self.gui_util = GuiUtil()
        

    # TODO : Add way to check if current_directory isn't git send Error
    def get_current_directory(self) -> str:
        return os.getcwd()
    
    def get_issueName(self) -> str :
        try:
            return Repo(self.cur_dir).active_branch.name
        except Exception as e:
            self.gui_util.show_dialog("Error", "cancel", "Current directory is not have .git", "OK")

    def get_git_detail(self):
        cur_log = Repo(self.cur_dir).active_branch.log()
        for entry in cur_log:
            print(f"{entry.message}   {datetime.fromtimestamp(entry.time[0])}" )
        return