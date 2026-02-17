import customtkinter as ctk
from constant.Enum import (TEXTSIZE, STORAGE,URL,WIDGET)
import util.common_util as common_util
from util.gui_util import GuiUtil
from util.jira_util import JiraUtil
import re
# TODO : REFACTOR , made it easier to read.
class ApiPage(ctk.CTkFrame):
        def __init__(
                      self,
                      parent : any
                      ):
               super().__init__(parent)
               self.gui_util = GuiUtil(self)
               self.show_title()
               self.body()
               self.submit_button()
                

        def show_title(self) -> None :
                title = ctk.CTkLabel(self,text="How to get API token",font=self.gui_util(TEXTSIZE.TEXT_LG.value))
                title.grid(row = 0, column = 0, padx = WIDGET.PAD_X.value, pady = WIDGET.PAD_Y.value)

        def body(self) -> None :
                self.step_frame()
                self.input_frame()

        def step_frame(self) -> None :
                step_frame = ctk.CTkFrame(self, fg_color="transparent")
                step_frame.grid(row=1,column=0, padx = WIDGET.PAD_X.value, pady = WIDGET.PAD_Y.value)
                steps = [
                "1. Go to Atlassian Account",
                "2. Click create API token",
                "3. Enter name and expiration date then create",
                "4. Click copy and paste in input field"
                ]
                for idx, text in enumerate(steps):
                        if(idx == 0):
                                label = self.gui_util.create_hyperlink_label(step_frame,text, TEXTSIZE.TEXT_SM, idx, 0, grid_args={"sticky":"w","padx":WIDGET.PAD_X.value,"pady":10})
                                label.bind("<Button-1>",lambda e:common_util.open_url(URL.JIRA_GET_API_URL.value))
                        else:
                                label = self.gui_util.create_normal_label(step_frame,text,TEXTSIZE.TEXT_SM,idx,0,grid_args={"sticky":"w","padx":WIDGET.PAD_X.value,"pady":10})

        def input_frame(self) -> None  :
                input_frame = ctk.CTkFrame(self, fg_color="transparent")
                input_frame.grid(row=1,column=1, padx = WIDGET.PAD_X.value, pady = WIDGET.PAD_Y.value)
                input_title = ctk.CTkLabel(input_frame, text="Jira Issue URL or Key", font=self.gui_util.font(TEXTSIZE.TEXT_MD.value))
                input_title.grid(row=0,column=0, pady = 5)
                self.email_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g. exmaple@gmail.com", width=300 , height= WIDGET.HEIGHT.value)
                self.email_entry.grid(row=1,column=0, pady = 5)
                self.api_token_entry = ctk.CTkEntry(input_frame, placeholder_text="API token",width=300 , height= WIDGET.HEIGHT.value, show="*")
                self.api_token_entry.grid(row=2,column=0, pady = 5)
                self.jira_url_entry = ctk.CTkEntry(input_frame, placeholder_text="Jira Site e.g. company.atlassian.net",width=300 , height= WIDGET.HEIGHT.value)
                self.jira_url_entry.grid(row=3,column=0, pady = 5)
                self.expire_date_entry = ctk.CTkEntry(input_frame, placeholder_text="Expiry date",width=300 , height= WIDGET.HEIGHT.value)
                self.expire_date_entry.grid(row=4,column=0, pady = 5)
                
        def submit_button(self) -> None :
                button = ctk.CTkButton(self,text="Confirm",command=self.store_api)
                button.grid(row=2,column=0,sticky="nsew", padx = 100, pady = 10)

        def store_api(self) -> None :
                email = self.email_entry.get()
                api = self.api_token_entry.get()
                url = self.jira_url_entry.get()
                expire_date = self.expire_date_entry.get()
                if(not email or not api or not url or not expire_date):
                        self.gui_util.show_dialog("Error", "cancel", "Please enter all input field.",options="OK")
                        return
                else:
                        data = {
                                "jira_email" : email,
                                "jira_api" : api,
                                "jira_prefix" : self.get_prefix(url),
                                "expire_date" : expire_date
                        }
                        response = common_util.get_user(email,api,url)
                        if(response.status_code != 200):
                                self.gui_util.show_dialog("Error", "cancel", "Can't fetch user from your input.",options="OK")
                                return
                        common_util.save_file(STORAGE.STORAGE_PATH.value,STORAGE.TOKEN_FILE.value,data)
                        self.after(0, self.master.show_worklog_page)
        def get_prefix(self, url):
                pattern = r'^(?:https?:\/?\/?)?([a-zA-Z0-9-]+)(?:\.atlassian\.net)?\/?$'
                match = re.match(pattern, url)
                if match:
                        return match.group(1)
                return None

