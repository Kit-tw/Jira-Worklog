import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import constant.constant as constant
import util.util as util

# TODO : REFACTOR , made it easier to read.
def jira_add_account_page(root):
    title = ttk.Label(root,text="How to get API token",font=util.font(constant.TEXT_LG))
    title.grid(row = 0, column = 0, sticky = W, pady = 2)

    step_frame = tk.Frame(root,height=150)
    stepOne = ttk.Label(step_frame,text= "1. Go to Atlassian Account" , font=util.font(constant.TEXT_SM),bootstyle=PRIMARY,cursor="hand2")
    stepOne.grid(row=0,column=0,sticky=W)
    stepOne.bind("<Button-1>", lambda e:util.opon_url(constant.JIRA_GET_API_URL))
    stepTwo = ttk.Label(step_frame,text="2. Click create API token", font=util.font(constant.TEXT_SM))
    stepTwo.grid(row=1,column=0,sticky=W)
    stepThree = ttk.Label(step_frame,text="3. Enter name and expiration date then create", font=util.font(constant.TEXT_SM))
    stepThree.grid(row=2,column=0,sticky=W)
    stepFour = ttk.Label(step_frame,text="4. Click copy and paste in input field", font=util.font(constant.TEXT_SM))
    stepFour.grid(row=3,column=0,sticky=W)
    step_frame.grid(row=1,column=0,sticky=W,pady=10,padx=20)

    #TODO: Research "CustomTkinter" might make it easier to implement
    input_frame = tk.Frame(root,height=150)
    input_title = ttk.Label(input_frame, text="Jira Issue URL or Key")
    input_title.grid(row=0,column=0,sticky=W)
    email_entry = ttk.Entry(input_frame)
    email_entry.grid(row=1,column=0,sticky=W)
    api_token_entry = ttk.Entry(input_frame)
    api_token_entry.grid(row=2,column=0,sticky=W)
    jira_url_entry = ttk.Entry(input_frame)
    jira_url_entry.grid(row=3,column=0,sticky=W)
    input_frame.grid(row=1,column=1,sticky=E,pady=10,padx=40)

    





    # ttk.Button(root, text = "Add account", bootstyle=INFO).pack(side=LEFT)