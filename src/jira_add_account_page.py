import customtkinter
import constant.constant as constant
import util.util as util

# TODO : REFACTOR , made it easier to read.
class api_page(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        #TODO : FIX 
        # show_title()
        # body()

        def show_title():
            title = customtkinter.CTkLabel(self,text="How to get API token",font=util.font(constant.TEXT_LG))
            title.grid(row = 0, column = 0, pady = 2)

        def body():
            step_frame()
            input_frame()
        #TODO : Loop
        def step_frame():
            step_frame = customtkinter.CTkFrame(self,height=150)
            stepOne = customtkinter.CTkLabel(step_frame,text= "1. Go to Atlassian Account" , font=util.font(constant.TEXT_SM),cursor="hand2")
            stepOne.grid(row=0,column=0,sticky='w')
            stepOne.bind("<Button-1>", lambda e:util.opon_url(constant.JIRA_GET_API_URL))
            stepTwo = customtkinter.CTkLabel(step_frame,text="2. Click create API token", font=util.font(constant.TEXT_SM))
            stepTwo.grid(row=1,column=0,sticky='w')
            stepThree = customtkinter.CTkLabel(step_frame,text="3. Enter name and expiration date then create", font=util.font(constant.TEXT_SM))
            stepThree.grid(row=2,column=0,sticky='w')
            stepFour = customtkinter.CTkLabel(step_frame,text="4. Click copy and paste in input field", font=util.font(constant.TEXT_SM))
            stepFour.grid(row=3,column=0,sticky='w')
            step_frame.grid(row=1,column=0,pady=10,padx=20)


        def input_frame():
            input_frame = customtkinter.CTkFrame(self,height=150)
            input_title = customtkinter.CTkLabel(input_frame, text="Jira Issue URL or Key")
            input_title.grid(row=0,column=0)
            email_entry = customtkinter.CTkEntry(input_frame)
            email_entry.grid(row=1,column=0)
            api_token_entry = customtkinter.CTkEntry(input_frame)
            api_token_entry.grid(row=2,column=0)
            jira_url_entry = customtkinter.CTkEntry(input_frame)
            jira_url_entry.grid(row=3,column=0)
            input_frame.grid(row=1,column=1,pady=10,padx=40)
