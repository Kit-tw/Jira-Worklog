import customtkinter as ctk
import constant.constant as constant
import util.util as util

# TODO : REFACTOR , made it easier to read.
class ApiPage(ctk.CTkFrame):
    def __init__(
                  self,
                  parent : any
                 ):
        super().__init__(parent)
        self.show_title()
        self.body()

    def show_title(self):
        self.title = ctk.CTkLabel(self,text="How to get API token",font=util.font(constant.TEXT_LG))
        self.title.grid(row = 0, column = 0, pady = 2)

    def body(self):
        self.step_frame()
        self.input_frame()
        #TODO : Loop
    def step_frame(self):
        self.step_frame = ctk.CTkFrame(self,height=150)
        self.stepOne = ctk.CTkLabel(self.step_frame,text= "1. Go to Atlassian Account" , font=util.font(constant.TEXT_SM),cursor="hand2")
        self.stepOne.grid(row=0,column=0,sticky='w')
        self.stepOne.bind("<Button-1>", lambda e:util.opon_url(constant.JIRA_GET_API_URL))
        self.stepTwo = ctk.CTkLabel(self.step_frame,text="2. Click create API token", font=util.font(constant.TEXT_SM))
        self.stepTwo.grid(row=1,column=0,sticky='w')
        self.stepThree = ctk.CTkLabel(self.step_frame,text="3. Enter name and expiration date then create", font=util.font(constant.TEXT_SM))
        self.stepThree.grid(row=2,column=0,sticky='w')
        self.stepFour = ctk.CTkLabel(self.step_frame,text="4. Click copy and paste in input field", font=util.font(constant.TEXT_SM))
        self.stepFour.grid(row=3,column=0,sticky='w')
        self.step_frame.grid(row=1,column=0,pady=10,padx=20)


    def input_frame(self):
        self.input_frame = ctk.CTkFrame(self,height=150)
        self.input_title = ctk.CTkLabel(self.input_frame, text="Jira Issue URL or Key")
        self.input_title.grid(row=0,column=0)
        self.email_entry = ctk.CTkEntry(self.input_frame)
        self.email_entry.grid(row=1,column=0)
        self.api_token_entry = ctk.CTkEntry(self.input_frame)
        self.api_token_entry.grid(row=2,column=0)
        self.jira_url_entry = ctk.CTkEntry(self.input_frame)
        self.jira_url_entry.grid(row=3,column=0)
        self.input_frame.grid(row=1,column=1,pady=10,padx=40)
