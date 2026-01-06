import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import constant.constant as constant
import util.util as util
from src.jira_add_account_page import jira_add_account_page

root = tk.Tk()
root.title("Worklog")
root.resizable(width=False,height=False)
root.geometry("500x500")
ttk.Frame(root, padding=(20,10,20,10))

if util.find(constant.TOKEN_PATH,constant.FILE_PATH):
    button = ttk.Button(root, text = "AccountFound ", bootstyle=INFO)
    button.pack(side=LEFT, padx=5, pady=10)
else:
    jira_add_account_page(root)
    




root.mainloop()