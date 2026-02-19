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
#TODO : FIX UI / grid configrue
class WorkLog(ctk.CTkFrame):
    ROW_TOOLTIP = 0
    ROW_INPUT = 1
    ROW_ISSUE = 2
    ROW_TIME = 3
    ROW_DATE = 4
    ROW_OPTIONS = 5
    ROW_FOOTER = 6
    MAX_COL_SPAN=3
    PLACEHOLDER_URL = "Jira Issue URL or Key"
    PLACEHOLDER_TIME = "Time spend e.g. 3h, 20m, 16s"
    PLACEHOLDER_DESCRIPTION = "Description"
    
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
        self.key_var = ctk.StringVar(self)
        self.date_var = ctk.StringVar(self, value=common_util.get_currentdate_forentry())
        self.time_var = ctk.StringVar(self)
        self.description_var = ctk.StringVar(self)
        self.worklog_history = common_util.get_worklog_history()
        self.header_frame()
        self.input_frame()
        self.body()
        self.grid_columnconfigure(0 , weight=1)
        self.grid_columnconfigure((1,2,3) , weight=2)
        

    def header_frame(self):
        self._header_tooltip()
        self._header_history()

    def _header_tooltip(self):
            img_path = common_util.find(STORAGE.IMAGE_PATH.value,STORAGE.TOOLTIP_IMAGE.value)
            img = ctk.CTkImage(light_image=Image.open(img_path),dark_image=Image.open(img_path),size=(30, 30))
            label = ctk.CTkLabel(self, image=img, text="", cursor="hand2")
            label.image = img
            label.bind("<Button-1>", lambda e: self.open_tooltip_toplevel())
            label.grid(row=self.ROW_TOOLTIP,column=self.MAX_COL_SPAN, sticky="nesw", pady=WIDGET.PAD_Y.value)

    def _header_history(self):
        if(len(self.worklog_history) > 0):
            history_dropdown = [item["summary"] for item in self.worklog_history]
            self._history_label = self.gui_util.create_normal_label(self,"Worklog History",TEXTSIZE.TEXT_X_SM,self.ROW_TOOLTIP,0,grid_args={"padx":WIDGET.PAD_X.value,"pady":WIDGET.PAD_Y.value})
            self._worklog_combobox = ctk.CTkComboBox(self, values=history_dropdown, width=300, height=WIDGET.HEIGHT.value, command=lambda e: self.open_worklog(self._worklog_combobox),font=self.gui_util.font(TEXTSIZE.TEXT_X_SM.value,underline=True))
            self._worklog_combobox.grid(row=self.ROW_TOOLTIP,column=1, sticky="n",padx=10,pady=WIDGET.PAD_Y.value)
            self._worklog_combobox.configure(text_color="#75add8")
            self._clear_history_btn = ctk.CTkButton(self,text="Clear History", command=self.clear_history, height=WIDGET.HEIGHT.value)
            self._clear_history_btn.grid(row=self.ROW_TOOLTIP,column=2, sticky="w",pady=WIDGET.PAD_Y.value)

    def clear_history(self):
        dialog = self.gui_util.show_dialog("Confirm", "warning", "Are you sure you want to clear history?", option_1="Yes", option_2="No")
        if(dialog.get() == "Yes"):
            common_util.delete_file(STORAGE.STORAGE_PATH.value, STORAGE.HISTORY_FILE.value)
            self._history_label.grid_remove()
            self._worklog_combobox.grid_remove()
            self._clear_history_btn.grid_remove()
            
    #TODO: FIX LOOP EVERYTIME CALLED
    def open_worklog(self,combobox : ctk.CTkComboBox):
        print(combobox.get())
        for item in self.worklog_history:
            if(item["summary"] == combobox.get()):
                combobox.bind("<Button-1>", lambda e : common_util.open_url(self.get_jira_url(item["key"])))
                self.key_var.set(item["key"])
                self.fetch_command(item["key"])
                break

    def get_jira_url(self, key):
        return self.jira_util.full_url + "/browse/" + key
        
    def input_frame(self):
        self.jira_url_entry = self.gui_util.create_entry_with_placeholder(self,self.PLACEHOLDER_URL,self.key_var,self.ROW_INPUT,0,entry_args={"width":WIDGET.WIDTH.value,"height":WIDGET.HEIGHT.value},grid_args={"sticky":"ew","padx":WIDGET.PAD_X.value,"pady":WIDGET.PAD_Y.value,"columnspan":self.MAX_COL_SPAN})
        fetch_btn = ctk.CTkButton(self,text="fetch",command=lambda : self.fetch_command(self.jira_url_entry.get()), height=WIDGET.HEIGHT.value)
        fetch_btn.grid(row=self.ROW_INPUT,column=3, sticky='ew',padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

    def fetch_command(self, key:str):
        self.issue_name =  self.jira_util.fetch_issue(key)
        if self.issue_name:
            self.issue_label.configure(text="Issue Name : " + self.issue_name,cursor="hand2")
            url = self.jira_util.full_url + "/browse/" + key
            self.issue_label.bind("<Button-1>", lambda e : common_util.open_url(url))
            return True
        return False

    def body(self):
        self.issue_label = self.gui_util.create_normal_label(self,"",TEXTSIZE.TEXT_X_SM,self.ROW_ISSUE,0,label_args={"text_color":"#75add8"},grid_args={"sticky":"nsew","columnspan":self.MAX_COL_SPAN})

        self.time_label = self.gui_util.create_normal_label(self,"Date & Time",TEXTSIZE.TEXT_SM,self.ROW_TIME,0,grid_args={"padx":WIDGET.PAD_X.value,"pady":WIDGET.PAD_Y.value})

        self.start_date_entry = CTkDateEntry(self, variable=self.date_var, height=WIDGET.HEIGHT.value)
        self.start_date_entry.grid(row=self.ROW_TIME, column=1, sticky='ew', padx=WIDGET.PAD_X.value)
      

        self.time_spend_entry = self.gui_util.create_entry_with_placeholder(self,self.PLACEHOLDER_TIME,self.time_var,self.ROW_TIME,2,entry_args={"height":WIDGET.HEIGHT.value},grid_args={"sticky":"ew","padx":WIDGET.PAD_X.value,"pady":WIDGET.PAD_Y.value,"columnspan":self.MAX_COL_SPAN})
        
        self.start_label = self.gui_util.create_normal_label(self,"Description",TEXTSIZE.TEXT_SM,self.ROW_DATE,0,grid_args={"padx":WIDGET.PAD_X.value})

        self.description_entry = self.gui_util.create_entry_with_placeholder(self,self.PLACEHOLDER_DESCRIPTION,self.description_var,self.ROW_DATE,1,entry_args={"height":WIDGET.HEIGHT.value},grid_args={"sticky":"ew","padx":WIDGET.PAD_X.value,"columnspan":self.MAX_COL_SPAN,"pady":WIDGET.PAD_Y.value})

        self.automate_label = self.gui_util.create_normal_label(self,"Automate Worklog",TEXTSIZE.TEXT_SM,self.ROW_OPTIONS,0,grid_args={"padx":WIDGET.PAD_X.value,"pady":WIDGET.PAD_Y.value})

        self.automate_options = ctk.CTkComboBox(self, values=["Manual","Git"], command=self.combobox_callback , height=WIDGET.HEIGHT.value)
        self.automate_options.grid(row=self.ROW_OPTIONS, column=1, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)

        self.insert_sheet = ctk.CTkCheckBox(self, text="Insert to sheet", font=self.gui_util.font(TEXTSIZE.TEXT_X_SM.value), command=self.checkbox_callback)
        self.insert_sheet.grid(row=self.ROW_OPTIONS, column=2, columnspan=2, padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)
        if(self.api_credentials):
            self.insert_sheet.select()

        self.confirm_btn = ctk.CTkButton(self, text="Confirm & Log Work", height=WIDGET.HEIGHT.value, command=self.insert_worklog)
        self.confirm_btn.grid(row=self.ROW_FOOTER, column=0, columnspan=1, sticky='w', padx=WIDGET.PAD_X.value, pady=WIDGET.PAD_Y.value)


    def insert_worklog(self) -> None:
        time_spend = self.time_spend_entry.get()
        date = self.date_var.get()
        description = self.description_entry.get()
        issue_key = self.jira_url_entry.get()
        is_insert_sheet = self.insert_sheet.get()

        if(not issue_key):
            self.gui_util.show_dialog("Error", "cancel", "Issue Key is not found", options="OK")
            return
        if(not self.fetch_command(issue_key)):
            self.gui_util.show_dialog("Error", "cancel", "Can't find issue by key", options="OK")
            return
        if(not time_spend or not re.match(REGEX.DATE.value,date)):
            self.gui_util.show_dialog("Error", "cancel", "Date and Time field required", options="OK")
            return
        date_time = common_util.date_str_to_iso(date)
        response = self.jira_util.post_insert_worklog(issue_key,time_spend,date_time,description)
        if(response.status_code != 201):
            if(is_insert_sheet):
                self.insert_to_sheet(issue_key,date,time_spend,description)
            self.save_history_json()
            dialog_msg = self.gui_util.show_dialog("Success", "check", "Worklog has been inserted", option_1="OK", option_2="View in Jira")
            if(dialog_msg.get() == "View in Jira"):
                common_util.open_url(self.get_jira_url(issue_key))

    def insert_to_sheet(self,
                        issue_key : str,
                        date : str,
                        time_spend : str,
                        description : str):
        if(not self.api_credentials):
            dialog_msg = self.gui_util.show_dialog("Warning","warning","google API in storage not found", option_1="Add", option_2="Exit")
            if(dialog_msg.get() == "Add"):
                self.open_googleapi_toplevel()
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
        return
    
    def git_insert_entry(self):
        git_util = GitUtil()
        key = git_util.get_issueName()
        if(key and self.fetch_command(key)):
           #TODO : add feature like the commit message and user can choose which commit to diff from previous log then auto fill description with commit message and time spend with time between 2 commit and date with commit date
           obj = git_util.get_git_detail()
           self.key_var.set(key)
           self.date_var.set(obj["date"])
           self.time_var.set(obj["time_spend"])
           self.description_var.set(obj["description"])


    def open_tooltip_toplevel(self):
        if self.tooltip_toplevel is None or not self.tooltip_toplevel.winfo_exists():
            self.tooltip_toplevel = ToolTip(self) 
        else:
            self.tooltip_toplevel.focus() 


    def save_history_json(self):
        if(len(self.worklog_history) > 0):
            history_keyset = set(item["key"] for item in self.worklog_history)
            if(self.key_var.get() in history_keyset):
                return
        json = {
            "key" : self.key_var.get(),
            "name" : self.issue_name,
            "summary" : f"{self.key_var.get()} : {self.issue_name}"
        }
        self.worklog_history.append(json)
        common_util.save_file(STORAGE.STORAGE_PATH.value,STORAGE.HISTORY_FILE.value,self.worklog_history,False)
        self._header_history()







            

    
