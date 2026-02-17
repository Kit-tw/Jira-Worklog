import customtkinter as ctk
import util.common_util as common_util
from constant.Enum import (STORAGE)
from customtkinter import filedialog

#TODO : UI HOW TO ADD API / LINK TO https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id
#TODO : DON'T FORGET TO ADD TEST USER BY YOUR EMAIL IN Audience

#TODO : Should Have 2 step 1. Oauth 2. User copy speadSheet then paste the open share then paste ID or URL to this app
class GoogleApiPage(ctk.CTkToplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.geometry("1000x500")
        self.title("API GOOGLE")
        self.transient(parent)
        self.resizable(width=False,height=False)
        self.input_frame()
    

    def input_frame(self):
        select_file_btn = ctk.CTkButton(self,text="Choose File",command=self.select_file)
        select_file_btn.grid()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files","*.JSON")])
        #VALIDATE BY OPEN FILE CHECK JSON
        dest_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_CREDENTIALS_FILE.value}"
        #TODO : IF upload success destroy top level
        common_util.copy_file(file_path,dest_path)

    