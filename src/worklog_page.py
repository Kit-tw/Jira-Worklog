import customtkinter as ctk
from util.jira_util import JiraUtil
class WorkLog(ctk.CTkFrame):
    def __init__(self,
                  parent : any):
        super().__init__(parent)
        self.jira_util = JiraUtil()
        self.issue_name=""
        self.input_frame()
        self.body()

    def input_frame(self):
        jira_url_entry = ctk.CTkEntry(self,placeholder_text="Jira Issue URL or Key")
        jira_url_entry.grid(row=0,column=0)
        fetch_btn = ctk.CTkButton(self,text="fetch",command=lambda : self.fetch_command(jira_url_entry.get()))
        fetch_btn.grid(row=0,column=1)

    def fetch_command(self, key:str):
        self.issue_name =  self.jira_util.fetch_issue(key)
        if self.issue_name:
            self.issue_label.configure(text="Issue Name : " + key + " " + self.issue_name)

    def body(self):
        self.issue_label = ctk.CTkLabel(self, text="")
        self.issue_label.grid(row=1, column=0)

    
