import customtkinter as ctk
from util.jira_util import JiraUtil

#TODO : NEW UI / grid configrue
class WorkLog(ctk.CTkFrame):
    ROW_INPUT = 0
    ROW_ISSUE = 1
    ROW_TIME = 2
    ROW_DATE = 3
    ROW_OPTIONS = 4
    ROW_FOOTER = 5

    def __init__(self,
                  parent : any):
        super().__init__(parent)
        self.jira_util = JiraUtil()
        self.issue_name=""
        self.input_frame()
        self.body()
        # self.hide_body_widgets()
        self.grid_columnconfigure(0 , weight=2)
        self.grid_columnconfigure((1, 2), weight=1)

    def input_frame(self):
        jira_url_entry = ctk.CTkEntry(self,placeholder_text="Jira Issue URL or Key")
        jira_url_entry.grid(row=self.ROW_INPUT,column=0, columnspan=1, sticky='ew')
        fetch_btn = ctk.CTkButton(self,text="fetch",command=lambda : self.fetch_command(jira_url_entry.get()))
        fetch_btn.grid(row=self.ROW_INPUT,column=1, columnspan=2)

    def fetch_command(self, key:str):
        self.issue_name = ""
        self.issue_name =  self.jira_util.fetch_issue(key)
        #TODO : if fetch_issue error hide_body_widget
        if self.issue_name:
            self.issue_label.configure(text="Issue Name : " + key + " " + self.issue_name)
            self.show_body_widgets()

    def body(self):
        self.issue_label = ctk.CTkLabel(self, text="")
        self.issue_label.grid(row=self.ROW_ISSUE, column=0, columnspan=3, sticky='nsew')

        self.time_label = ctk.CTkLabel(self, text="Time")
        self.time_label.grid(row=self.ROW_TIME, column=0)

        self.time_spend_entry = ctk.CTkEntry(self)
        self.time_spend_entry.grid(row=self.ROW_TIME, column=1)

        self.time_remaining_entry = ctk.CTkEntry(self)
        self.time_remaining_entry.grid(row=self.ROW_TIME, column=2)

        self.start_label = ctk.CTkLabel(self, text="Date & Description")
        self.start_label.grid(row=self.ROW_DATE, column=0)

        self.start_date_entry = ctk.CTkEntry(self)
        self.start_date_entry.grid(row=self.ROW_DATE, column=1)

        self.description_entry = ctk.CTkEntry(self)
        self.description_entry.grid(row=self.ROW_DATE, column=2)

        self.automate_label = ctk.CTkLabel(self, text="Automate Worklog")
        self.automate_label.grid(row=self.ROW_OPTIONS, column=0)

        self.automate_options = ctk.CTkComboBox(self, values=["Manual","Git","Jira"])
        self.automate_options.grid(row=self.ROW_OPTIONS, column=1)

        self.insert_sheet = ctk.CTkCheckBox(self, text="Insert to google sheets")
        self.insert_sheet.grid(row=self.ROW_OPTIONS, column=2)

        self.confirm_btn = ctk.CTkButton(self, text="Confirm & Log Work")
        self.confirm_btn.grid(row=self.ROW_FOOTER, column=0, columnspan=1, sticky='w')


    def hide_body_widgets(self):
         for widget in (
            self.issue_label,
            self.time_label,
            self.time_spend_entry,
            self.time_remaining_entry,
            self.start_label,
            self.start_date_entry,
            self.description_entry,
            self.automate_label,
            self.automate_options,
            self.insert_sheet,
            self.confirm_btn
        ):
             widget.grid_remove()

    def show_body_widgets(self):
        for widget in (
            self.issue_label,
            self.time_label,
            self.time_spend_entry,
            self.time_remaining_entry,
            self.start_label,
            self.start_date_entry,
            self.description_entry,
            self.automate_label,
            self.automate_options,
            self.insert_sheet,
            self.confirm_btn
        ):
            widget.grid()








            

    
