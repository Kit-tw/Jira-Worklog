import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import constant.constant as constant
import util.util as util

# TODO : REFACTOR , made it easier to read.
def jira_add_account_page(root):
    ttk.Label(root,text="Account not found",font=util.font(constant.TEXT_LG)).pack(side=TOP)
    ttk.Label(root,text="Step",font=util.font(constant.TEXT_SM)).pack(anchor='w')
    label =ttk.Label(root,text= "1. Log in to" + constant.JIRA_GET_API_URL , font=util.font(constant.TEXT_X_SM),bootstyle=PRIMARY,cursor="hand2")
    label.pack(anchor='w')
    label.bind("<Button-1>", lambda e:util.opon_url(constant.JIRA_GET_API_URL))
    ttk.Label(root,text="2. Click create API token").pack(anchor='w')
    ttk.Label(root,text="3. From the dialog that appears, enter a memorable and concise Label for your token and click Create").pack(anchor='w')
    ttk.Label(root,text="4. Click copy and paste in input field").pack(anchor='w')
    ttk.Button(root, text = "Add account", bootstyle=INFO).pack(side=LEFT)