import re
import customtkinter as ctk
import util.common_util as common_util
from constant.Enum import (STORAGE, TEXTSIZE, URL, WIDGET)
from util.gui_util import GuiUtil
from customtkinter import filedialog

class GoogleApiPage(ctk.CTkToplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.geometry("1000x500")
        self.title("API GOOGLE")
        self.transient(parent)
        self.resizable(width=False,height=False)
        self.gui_util = GuiUtil(self)
        self._header_ui()
        self.body()
        self.input_frame()
        self.grid_columnconfigure((0,1), weight=1)
    


    def _header_ui(self) -> None :
                self.gui_util.create_normal_label(self,"How to get API token",TEXTSIZE.TEXT_MD,0,0,grid_args={"padx":WIDGET.PAD_X.value,"pady":WIDGET.PAD_Y.value})
                hyperlink = self.gui_util.create_hyperlink_label(self,"Reference Documentation",TEXTSIZE.TEXT_SM,0,1,grid_args={"pady":WIDGET.PAD_Y.value})
                hyperlink.bind("<Button-1>",lambda e:common_util.open_url(URL.GSPREAD_GOOGLE_API_DOC.value))

    def body(self) -> None :
            self.step_frame()
    def step_frame(self) -> None :
            step_frame = ctk.CTkFrame(self, fg_color="transparent")
            step_frame.grid(row=1,column=0, padx = WIDGET.PAD_X.value, pady = WIDGET.PAD_Y.value)
            steps = [
            "1. Go to Google Developer Console",
            "2. create project and enable Google Sheets, Drive API, then create credentials for OAuth client ID",
            "3. create test user and add email in Audience when create credential",
            "4. Download the credential and upload to this app"
            ]
            for idx, text in enumerate(steps):
                    if(idx == 0):
                            label = self.gui_util.create_hyperlink_label(step_frame,text, TEXTSIZE.TEXT_X_SM, idx, 0, grid_args={"sticky":"w","pady":10})
                            label.bind("<Button-1>",lambda e:common_util.open_url(URL.GOOGLE_DEVELOPER_CONSOLE.value))
                    else:
                            label = self.gui_util.create_normal_label(step_frame,text,TEXTSIZE.TEXT_X_SM,idx,0,grid_args={"sticky":"w","pady":10})

    def input_frame(self):
        select_file_btn = ctk.CTkButton(self,text="Choose File",command=self.select_file, width=200, height=WIDGET.HEIGHT.value)
        select_file_btn.grid()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files","*.JSON")])
        dest_path = f"{STORAGE.STORAGE_PATH.value}/{STORAGE.GOOGLE_API_CREDENTIALS_FILE.value}"
        if self.validate_credential(file_path):
            common_util.copy_file(file_path,dest_path)
            self.destroy()
    
    def validate_credential(self, file_path):
        try:
            regex = "(client_id).*(project_id)"
            read_json = common_util.read_json_file_by_full_path(file_path)
            if read_json is not None and re.search(regex, str(read_json)):
                return True
            else:
                raise ValueError("Invalid credential file")
        except Exception as e:
            print(e)
            GuiUtil().show_dialog("Error", "cancel", "Failed to read credential file. Please make sure it's a valid JSON file.", options="OK")
            return False

    