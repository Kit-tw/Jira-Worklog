from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
# def hyperlink(root,text,url):

class GuiUtil:
    def __init__(self,parent=None):
         self.parent = parent

    def show_dialog(self, title, icon, text, *options):
        CTkMessagebox(
            title=title,
            message=text,
            icon=icon,
            options=options
        )
        
        


