import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import constant.constant as constant
import util.util as util

def jira_add_account_page(root):
    ttk.Label(root,text="Account not found",font=util.font(constant.TEXT_LG), bootstyle=DEFAULT).pack(side=TOP, pady=10)
    ttk.Label(root,text="Step",font=util.font(constant.TEXT_SM),bootstyle=DEFAULT).pack(anchor='w', padx=20)
    ttk.Label(root,text= "1. Log in to", font=util.font(constant.TEXT_X_SM),bootstyle=DEFAULT,Wrap='none').pack(anchor="w",padx=20)
    ttk.Button(root, text = "Add account", bootstyle=INFO).pack(side=LEFT, padx=5, pady=10)