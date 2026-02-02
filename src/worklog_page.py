import customtkinter as ctk
from util.jira_util import JiraUtil
from util.git_util import GitUtil
from util.gui_util import GuiUtil
from util.sheets_util import SheetsUtil
from src.tooltip_toplevel import ToolTip
from src.google_api_add_page import GoogleApiPage
import util.common_util as common_util
from constant.Enum import (TEXTSIZE,WIDGET,REGEX,STORAGE)
from ctkdateentry import CTkDateEntry, CTkStringVar
import re
from PIL import Image
#TODO : ADD BUTTON FOR DELETE STORAGE FILE
#TODO : NEW UI / grid configrue
class WorkLog(ctk.CTkFrame):
    ROW_TOOLTIP = 0
    ROW_INPUT = 1
    ROW_ISSUE = 2
    ROW_TIME = 3
    ROW_DATE = 4
    ROW_OPTIONS = 5
    ROW_FOOTER = 6
    MAX_COL_SPAN=3
    
#TODO: Should use save jira Link if fetch issue success? then display as dropdown for next time use
#TODO : ADD WORKLOG HISTORY PAGE BELOW SUBMIT BUTTON
    def __init__(self,
                  parent : any):
        super().__init__(parent)
        self.jira_util = JiraUtil()
        self.gui_util = GuiUtil(self)
        self.api_authorized = common_util.find(STORAGE.STORAGE_PATH.value,STORAGE.GOOGLE_API_AUTHORIZED_USER_FILE.value)
        self.api_credentials =  common_util.find(STORAGE.STORAGE_PATH.value,STORAGE.GOOGLE_API_CREDENTIALS_FILE.value)
        self.toplevel_google_api = None
        self.tooltip_toplevel = None
        self.issue_name=""
        self.date_entry = CTkStringVar(self, value= "Date")
        self.tooltip_frame()
        self.input_frame()
        self.body()
        # self.hide_body_widgets()
        self.grid_columnconfigure(0 , weight=1)
        self.grid_columnconfigure((1,2,3) , weight=2)
        

    def tooltip_frame(self):
        img_path = common_util.find(STORAGE.IMAGE_PATH.value,STORAGE.TOOLTIP_IMAGE.value)
        img = ctk.CTkImage(light_image=Image.open(img_path),dark_image=Image.open(img_path),size=(50, 50))
        label = ctk.CTkLabel(self, image=img, text="")
        label.image = img
        label.bind("<Button-1>", lambda e: self.open_tooltip_toplevel())
        label.grid(row=self.ROW_TOOLTIP,column=self.MAX_COL_SPAN,columnspan=3, sticky="e")

    def input_frame(self):
        self.jira_url_entry = ctk.CTkEntry(self,placeholder_text="Jira Issue URL or Key", width=WIDGET.WIDTH.value, height=WIDGET.HEIGHT.value)
        self.jira_url_entry.grid(row=self.ROW_INPUT,column=0, sticky='ew',padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value, columnspan=self.MAX_COL_SPAN)
        fetch_btn = ctk.CTkButton(self,text="fetch",command=lambda : self.fetch_command(self.jira_url_entry.get()), height=WIDGET.HEIGHT.value)
        fetch_btn.grid(row=self.ROW_INPUT,column=3, sticky='ew',padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

    def fetch_command(self, key:str):
        self.issue_name = ""
        self.issue_name =  self.jira_util.fetch_issue(key)
        if self.issue_name:
            self.issue_label.configure(text="Issue Name : " + self.issue_name)
            self.show_body_widgets()

    #TODO : Should use scroll bar for adding multiple log then move last grid section to footer
    #TODO : IF you add scroll bar you have to add delete button for if section > 1
    def body(self):
        self.issue_label = ctk.CTkLabel(self, text="", font=common_util.font(TEXTSIZE.TEXT_MD.value), text_color="lightblue")
        self.issue_label.grid(row=self.ROW_ISSUE, column=0, sticky='nsew',columnspan=self.MAX_COL_SPAN)

        self.time_label = ctk.CTkLabel(self, text="Date & Time", font=common_util.font(TEXTSIZE.TEXT_SM.value))
        self.time_label.grid(row=self.ROW_TIME, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.start_date_entry = CTkDateEntry(self, variable=self.date_entry, height=WIDGET.HEIGHT.value)
        self.start_date_entry.grid(row=self.ROW_TIME, column=1, sticky='ew', padx=WIDGET.PAD_X.value)

        self.time_spend_entry = ctk.CTkEntry(self, placeholder_text="Time spend e.g. 3h, 20m, 16s", height=WIDGET.HEIGHT.value)
        self.time_spend_entry.grid(row=self.ROW_TIME, column=2, sticky='ew', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value,  columnspan=self.MAX_COL_SPAN)


        self.start_label = ctk.CTkLabel(self, text="Description", font=common_util.font(TEXTSIZE.TEXT_SM.value))
        self.start_label.grid(row=self.ROW_DATE, column=0, padx=WIDGET.PAD_X.value)


        self.description_entry = ctk.CTkEntry(self,placeholder_text="Description", height=WIDGET.HEIGHT.value)
        self.description_entry.grid(row=self.ROW_DATE, column=1, sticky='ew', padx=WIDGET.PAD_X.value, columnspan=self.MAX_COL_SPAN)

        self.automate_label = ctk.CTkLabel(self, text="Automate Worklog", font=common_util.font(TEXTSIZE.TEXT_SM.value))
        self.automate_label.grid(row=self.ROW_OPTIONS, column=0, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)
        #TODO : IF select Git can choose maximum hour for automate insert and if select git the max range where section can have is 5
        #TODO : Jira can check from history status
        self.automate_options = ctk.CTkComboBox(self, values=["Manual","Git","Jira"], command=self.combobox_callback)
        self.automate_options.grid(row=self.ROW_OPTIONS, column=1, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        #TODO: ADD when having sheet ID add label link to that spread sheet link
        self.insert_sheet = ctk.CTkCheckBox(self, text="Insert to google sheets", font=common_util.font(TEXTSIZE.TEXT_X_SM.value), command=self.checkbox_callback)
        self.insert_sheet.grid(row=self.ROW_OPTIONS, column=2, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.confirm_btn = ctk.CTkButton(self, text="Confirm & Log Work", height=WIDGET.HEIGHT.value, command=self.insert_worklog)
        self.confirm_btn.grid(row=self.ROW_FOOTER, column=0, columnspan=1, sticky='w', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)


    def hide_body_widgets(self):
         for widget in (
            self.issue_label,
            self.time_label,
            self.time_spend_entry,
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
            self.start_label,
            self.start_date_entry,
            self.description_entry,
            self.automate_label,
            self.automate_options,
            self.insert_sheet,
            self.confirm_btn
        ):
            widget.grid()

    def insert_worklog(self) -> None:
        time_spend = self.time_spend_entry.get()
        date = self.date_entry.get()
        description = self.description_entry.get()
        issue_key = self.jira_url_entry.get()
        is_insert_sheet = self.insert_sheet.get()

        # if(not issue_key):
        #     self.gui_util.show_dialog("Error", "cancel", "Issue Key is not found", options="OK")
        #     return
        # if(not time_spend or not re.match(REGEX.DATE.value,date)):
        #     self.gui_util.show_dialog("Error", "cancel", "Date and Time field required", options="OK")
        #     return
        #TODO : IF TOP LEVEL IS Aleady OPEN then check the path in this too
        # date_time = common_util.date_str_to_iso(date)
        # TODO : handle response if success provide JIRA URL if checkbox is check provide link to google sheets
        # TODO : IF DIALOG "OK" is click clear all input field
        # response = self.jira_util.post_insert_worklog(issue_key,time_spend,date_time,description)
        # print(response.text)
        if(is_insert_sheet):
            self.insert_to_sheet(issue_key,date,time_spend,description)

    #TODO : SHOULD CHECK EXIST Sheets too
    def insert_to_sheet(self,
                        issue_key : str,
                        date : str,
                        time_spend : str,
                        description : str):
        if(not self.api_authorized or not self.api_credentials):
            #TODO : Throw to insert google API page 
            return
        SheetsUtil(key=issue_key,date=date,time=time_spend,description=description)
    
    def checkbox_callback(self):
        checkbox_value = self.insert_sheet.get()
        if(checkbox_value and self.toplevel_google_api is None and (not self.api_credentials)):
            dialog_msg = self.gui_util.show_dialog("Warning","warning","google API in storage not found", option_1="Add", option_2="Exit")
            if(dialog_msg.get() == "Add"):
                self.open_googleapi_toplevel()
            else:
                self.insert_sheet.deselect()
                
            
    def open_googleapi_toplevel(self):
        if self.toplevel_google_api is None or not self.toplevel_google_api.winfo_exists():
            self.toplevel_google_api = GoogleApiPage(self) 
        else:
            self.toplevel_google_api.focus() 

    def combobox_callback(self,choice):
        if(choice == "Git"):
            return self.git_insert_entry()
        if (choice == "Jira"):
            return
        return
    
    def git_insert_entry(self):
        git_util = GitUtil()
        print(git_util.get_issueName())
        print(git_util.get_git_detail())

    def open_tooltip_toplevel(self):
        if self.tooltip_toplevel is None or not self.tooltip_toplevel.winfo_exists():
            self.tooltip_toplevel = ToolTip(self) 
        else:
            self.tooltip_toplevel.focus() 






            

    
