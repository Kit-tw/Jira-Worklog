import customtkinter as ctk
import util.common_util as common_util
from constant.Enum import (STORAGE)
from customtkinter import filedialog
class GoogleApiPage(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1000x500")
        self.title("API GOOGLE")
        self.resizable(width=False,height=False)
        self.input_frame()
    

    def input_frame(self):
        select_file_btn = ctk.CTkButton(self,text="Choose File",command=self.select_file)
        select_file_btn.grid()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files","*.JSON")])
        #VALIDATE BY OPEN FILE CHECK JSON
        dest_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_CREDENTIALS_FILE.value}"
        common_util.copy_file(file_path,dest_path)

    