import customtkinter
import constant.constant as constant
import util.util as util
from src.jira_add_account_page import api_page

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Worklog")
        self.resizable(width=False,height=False)
        self.geometry("1000x500")

        if util.find(constant.TOKEN_PATH,constant.FILE_PATH):
            button =  customtkinter.CTkButton(self, text= "Ready to log", bg_color="blue")
            button.pack(padx=5, pady=10)
        else:
            api_page(self)

app = App()
app.mainloop()