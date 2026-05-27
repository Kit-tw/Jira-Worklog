import sys
import asyncio

cli_flags = {"-ga", "-gm", "-m"}
if any(flag in sys.argv for flag in cli_flags):
    from util.cli_util import JiraWorklogCLI
    asyncio.run(JiraWorklogCLI().run())
    sys.exit(0)

import customtkinter as ctk
import util.file_util as file_util
import util.common_util as common_util
from constant.Enum import STORAGE
from util.gui_util import GuiUtil
from src.jira_add_account_page import ApiPage
from src.worklog_page import WorkLog


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Worklog")
        self.resizable(width=False, height=False)
        self.geometry("1000x500")
        ctk.set_appearance_mode("dark")
        self.current_page = None
        self.show_initial_page()

    def show_initial_page(self):
        if self._jira_api_valid():
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

    def _jira_api_valid(self) -> bool:
        if not file_util.find(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value):
            return False
        return self._validate_expire_date()

    def _validate_expire_date(self) -> bool:
        try:
            info = file_util.read_json(STORAGE.STORAGE_PATH.value, STORAGE.TOKEN_FILE.value)
        except Exception:
            return False
        if common_util.now_greater_than_date(info["expire_date"], "%d/%m/%Y"):
            dialog = GuiUtil().show_dialog("Info", "check", "Jira API token has expired", option_1="OK")
            if dialog.get() == "OK":
                return False
        return True


if __name__ == "__main__":
    app = App()
    app.mainloop()
