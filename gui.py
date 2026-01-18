import customtkinter as ctk
from constant.Enum import (STORAGE) 
import util.common_util as common_util
from src.jira_add_account_page import ApiPage
from src.worklog_page import WorkLog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Worklog")
        self.resizable(width=False,height=False)
        self.geometry("1000x500")


        if not common_util.find(STORAGE.STORAGE_PATH.value,STORAGE.TOKEN_FILE.value):
            worklog_page = WorkLog(self)
            worklog_page.pack(fill="both",expand=True)
        else:
            api_page = ApiPage(self)
            api_page.pack(fill="both",expand=True)

app = App()
app.mainloop()