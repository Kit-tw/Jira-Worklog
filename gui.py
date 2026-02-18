import customtkinter as ctk
from constant.Enum import (STORAGE) 
import util.common_util as common_util
from util.gui_util import GuiUtil
from src.jira_add_account_page import ApiPage
from src.worklog_page import WorkLog
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Worklog")
        self.resizable(width=False,height=False)
        self.geometry("1000x500")
        ctk.set_appearance_mode("dark")

        self.current_page = None
        self.show_initial_page()

    def show_initial_page(self):
        if self.jira_api_valid():
            self.show_worklog_page()
        else:
            self.show_api_page()

    def clear_page(self):
        if self.current_page:
            self.current_page.destroy()

    def show_api_page(self):
        self.clear_page()
        self.current_page = ApiPage(self)
        self.current_page.pack(fill="both", expand=True)

    def show_worklog_page(self):
        self.clear_page()
        self.current_page = WorkLog(self)
        self.current_page.pack(fill="both", expand=True)

    def jira_api_valid(self):
        return common_util.find(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value) and self.validate_expire_date()
        
    def validate_expire_date(self):
        info = common_util.read_json_file(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        if(common_util.now_greater_than_date(info["expire_date"])):
            dialog_msg = GuiUtil().show_dialog("Info", "check", "Jira API token has expired", option_1="OK")
            if(dialog_msg.get() == "OK"):
                return False
        return True

app = App()
app.mainloop()