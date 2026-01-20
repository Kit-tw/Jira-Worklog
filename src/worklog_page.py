import customtkinter as ctk
from util.jira_util import JiraUtil
from constant.Enum import (TEXTSIZE,WIDGET)
import util.common_util as common_util

#TODO : NEW UI / grid configrue
class WorkLog(ctk.CTkFrame):
    ROW_INPUT = 0
    ROW_ISSUE = 1
    ROW_TIME = 2
    ROW_DATE = 3
    ROW_OPTIONS = 4
    ROW_FOOTER = 5
    MAX_COL_SPAN=3
    

    def __init__(self,
                  parent : any):
        super().__init__(parent)
        self.jira_util = JiraUtil()
        self.issue_name=""
        self.input_frame()
        self.body()
        # self.hide_body_widgets()
        self.grid_columnconfigure(0 , weight=1)
        self.grid_columnconfigure((1,2,3) , weight=2)

    def input_frame(self):
        jira_url_entry = ctk.CTkEntry(self,placeholder_text="Jira Issue URL or Key", width=WIDGET.WIDTH.value, height=WIDGET.HEIGHT.value)
        jira_url_entry.grid(row=self.ROW_INPUT,column=0, sticky='ew',padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value, columnspan=3)
        fetch_btn = ctk.CTkButton(self,text="fetch",command=lambda : self.fetch_command(jira_url_entry.get()), height=WIDGET.HEIGHT.value)
        fetch_btn.grid(row=self.ROW_INPUT,column=3, sticky='ew',padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

    def fetch_command(self, key:str):
        self.issue_name = ""
        self.issue_name =  self.jira_util.fetch_issue(key)
        #TODO : if fetch_issue error hide_body_widget
        if self.issue_name:
            self.issue_label.configure(text="Issue Name : " + self.issue_name)
            self.show_body_widgets()

    def body(self):
        self.issue_label = ctk.CTkLabel(self, text="", font=common_util.font(TEXTSIZE.TEXT_MD.value), text_color="lightblue")
        self.issue_label.grid(row=self.ROW_ISSUE, column=0, sticky='nsew',columnspan=self.MAX_COL_SPAN)

        self.time_label = ctk.CTkLabel(self, text="Date & Time", font=common_util.font(TEXTSIZE.TEXT_SM.value))
        self.time_label.grid(row=self.ROW_TIME, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.start_date_entry = ctk.CTkEntry(self, placeholder_text="Date", height=WIDGET.HEIGHT.value)
        self.start_date_entry.grid(row=self.ROW_TIME, column=1, sticky='ew', padx=WIDGET.PAD_X.value)

        self.time_spend_entry = ctk.CTkEntry(self, placeholder_text="Time spend e.g. 2w, 1d, 3h, 20m, 16s", height=WIDGET.HEIGHT.value)
        self.time_spend_entry.grid(row=self.ROW_TIME, column=2, sticky='ew', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value,  columnspan=self.MAX_COL_SPAN)


        self.start_label = ctk.CTkLabel(self, text="Description", font=common_util.font(TEXTSIZE.TEXT_SM.value))
        self.start_label.grid(row=self.ROW_DATE, column=0, padx=WIDGET.PAD_X.value)


        self.description_entry = ctk.CTkEntry(self,placeholder_text="Description", height=WIDGET.HEIGHT.value)
        self.description_entry.grid(row=self.ROW_DATE, column=1, sticky='ew', padx=WIDGET.PAD_X.value, columnspan=self.MAX_COL_SPAN)

        self.automate_label = ctk.CTkLabel(self, text="Automate Worklog", font=common_util.font(TEXTSIZE.TEXT_SM.value))
        self.automate_label.grid(row=self.ROW_OPTIONS, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.automate_options = ctk.CTkComboBox(self, values=["Manual","Git","Jira"])
        self.automate_options.grid(row=self.ROW_OPTIONS, column=1, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.insert_sheet = ctk.CTkCheckBox(self, text="Insert to google sheets", font=common_util.font(TEXTSIZE.TEXT_X_SM.value))
        self.insert_sheet.grid(row=self.ROW_OPTIONS, column=2, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.confirm_btn = ctk.CTkButton(self, text="Confirm & Log Work", height=WIDGET.HEIGHT.value)
        self.confirm_btn.grid(row=self.ROW_FOOTER, column=0, columnspan=1, sticky='w', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)


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








            

    
