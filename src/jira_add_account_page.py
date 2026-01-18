import customtkinter as ctk
import constant.constant as constant
import util.util as util

# TODO : REFACTOR , made it easier to read.
# TODO : NEW UI 
# TODO : make core function check for option hypertext, text, error (red color text)
class ApiPage(ctk.CTkFrame):
        def __init__(
                      self,
                      parent : any
                      ):
               super().__init__(parent)
               self.show_title()
               self.body()
               self.submit_button()
               self.grid_columnconfigure((0, 1), weight=1)
               self.grid_rowconfigure((0, 1, 2), weight=1)
                

        def show_title(self) -> None :
                title = ctk.CTkLabel(self,text="How to get API token",font=util.font(constant.TEXT_LG))
                title.grid(row = 0, column = 0, pady = 2)

        def body(self) -> None :
                self.step_frame()
                self.input_frame()

                #TODO : Make steps -> Object with option for hyperLink | text if equal hyperLink use hyperLink function
        def step_frame(self) -> None :
                step_frame = ctk.CTkFrame(self)
                step_frame.grid(row=1,column=0,pady=10,padx=20)
                step_frame.grid_propagate(0)
                steps = [
                "1. Go to Atlassian Account",
                "2. Click create API token",
                "3. Enter name and expiration date then create",
                "4. Click copy and paste in input field"
                ]
                for idx, text in enumerate(steps):
                        if(idx == 0):
                                label = ctk.CTkLabel(step_frame,text=text,font=util.font(constant.TEXT_SM),cursor="hand2")
                                label.bind("<Button-1>",lambda e:util.opon_url(constant.JIRA_GET_API_URL))
                                label.grid(row=idx,column=0,sticky='w')
                        else:
                                label = ctk.CTkLabel(step_frame,text=text, font=util.font(constant.TEXT_SM))
                                label.grid(row=idx,column=0,sticky='w')

        def input_frame(self) -> None  :
                input_frame = ctk.CTkFrame(self)
                input_frame.grid(row=1,column=1,pady=10,padx=40)
                input_frame.grid_propagate(0)
                input_title = ctk.CTkLabel(input_frame, text="Jira Issue URL or Key", font=util.font(constant.TEXT_MD))
                input_title.grid(row=0,column=0)
                self.email_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g. exmaple@gmail.com", width=300 , height= 30)
                self.email_entry.grid(row=1,column=0)
                self.api_token_entry = ctk.CTkEntry(input_frame, placeholder_text="API token",width=300 , height= 30, show="*")
                self.api_token_entry.grid(row=2,column=0)
                self.jira_url_entry = ctk.CTkEntry(input_frame, placeholder_text="Jira Site e.g. company.atlassian.net",width=300 , height= 30)
                self.jira_url_entry.grid(row=3,column=0)
                
        def submit_button(self) -> None :
                button = ctk.CTkButton(self,text="Confirm",command=self.store_api)
                button.grid(row=2,column=0)

        def store_api(self) -> None :
                email = self.email_entry.get()
                api = self.api_token_entry.get()
                url = self.jira_url_entry.get()
                if(not email or not api or not url):
                        ctk.CTkLabel(self,text="Please enter all input field.").grid(row=4,column=0)
                else:
                        data = {
                                "jira_email" : email,
                                "jira_api" : api,
                                "jira_url" : url 
                        }
                        util.save_json_file(constant.STORAGE_PATH,"token",data)
                        
