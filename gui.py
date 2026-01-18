import customtkinter as ctk
import constant.constant as constant
import util.util as util
from src.jira_add_account_page import ApiPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Worklog")
        self.resizable(width=False,height=False)
        self.geometry("1000x500")


        if util.find(constant.TOKEN_PATH,constant.FILE_PATH):
            button =  ctk.CTkButton(self, text= "Ready to log", bg_color="blue")
            button.pack(padx=5, pady=10)
        else:
            api_page = ApiPage(self)
            api_page.pack(fill="both",expand=True)

app = App()
app.mainloop()