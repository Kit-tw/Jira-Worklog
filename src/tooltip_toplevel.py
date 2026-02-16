import customtkinter as ctk
from constant.Enum import (STORAGE,WIDGET)
from util.jira_util import JiraUtil
import util.common_util as common_util
import os
import subprocess
class ToolTip(ctk.CTkToplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.title("Information")
        self.transient(parent)        
        self.resizable(width=False,height=False)
        self.jira_info = JiraUtil()
        self.sheet_link = ""
        self.frame()

    def frame(self):
        key = [
             ("Jira Email : " , self.jira_info.mail, None),
             ("Jira Site : " , self.jira_info.prefix_url, lambda: common_util.open_url(self.jira_info.full_url)),
             ("Store file path : " , STORAGE.STORAGE_PATH.value, lambda: self.open_explorer(STORAGE.STORAGE_PATH.value)),
             ]
        if(common_util.find(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value)):
            info = common_util.read_json_file(STORAGE.STORAGE_PATH.value,STORAGE.INFORMATION_FILE.value)
            get_sheet_url = self.get_sheet_url(info['spreadsheetId'])
            key.append(("Google Sheet Link : ", "Open",lambda: common_util.open_url(get_sheet_url)))
        
        self.info_section(key)
        return
    
    def get_sheet_url(self,spreadsheet_id):
        self.sheet_link = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        return self.sheet_link
    
    def info_section(self,
                     list : list
                     ):
        row = 0
        for _key, _value, action in list :
            ctk.CTkLabel(self,text=_key).grid(row=row,column = 0,padx= WIDGET.PAD_X.value)
            value = ctk.CTkLabel(self,text=_value)
            if callable(action):
                value.bind(
                    "<Button-1>",
                    lambda e, fn=action: fn()
                )
                value.configure(cursor="hand2",text_color="#1f6aa5")
            value.grid(row=row,column = 1,padx= WIDGET.PAD_X.value)
            row = row + 1
        return
    
    def open_explorer(self, path):
        path = os.path.normpath(path.strip())

        if os.path.isdir(path):
            subprocess.Popen(['explorer', path])
        elif os.path.isfile(path):
            subprocess.Popen(['explorer', '/select,', path])
        else:
            print("Invalid path:", repr(path))

    
    def open_sheet(self, value : ctk.CTkLabel):
        value.bind("<Button-1>",lambda e:common_util.open_url(self.sheet_link))