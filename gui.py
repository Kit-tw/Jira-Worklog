import customtkinter as ctk
from constant.Enum import (STORAGE) 
import util.common_util as common_util
from src.jira_add_account_page import ApiPage
from src.worklog_page import WorkLog
#TODO : CHECK expire date of API if expire date is greater remove file and show jira api page again
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
        if common_util.find(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value):
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

app = App()
app.mainloop()