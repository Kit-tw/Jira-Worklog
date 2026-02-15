from CTkMessagebox import CTkMessagebox
import customtkinter as ctk
from constant.Enum import (WIDGET,TEXTSIZE)
from ctkdateentry import CTkDateEntry, CTkStringVar
# def hyperlink(root,text,url):

class GuiUtil:
    def __init__(self,parent=None):
         self.parent = parent

    def show_dialog(self, title, icon, text, **options):
        return CTkMessagebox(
            title=title,
            message=text,
            icon=icon,
            **options
        )
    

    def create_entry_with_description(self,master,description,var,sticky)-> ctk.CTkFrame:
        new_frame = ctk.CTkFrame(master, fg_color="transparent")
        row = 0
        if(description):
            self.create_normal_label(new_frame,description,TEXTSIZE.TEXT_X_SM,row,0,grid_args={"padx":WIDGET.PAD_X.value})
            row = row + 1
        ctk.CTkEntry(new_frame,textvariable=var,height=WIDGET.HEIGHT.value).grid(row=row, column=0, padx=WIDGET.PAD_X.value,sticky=sticky)
        return new_frame
    
    def create_date_entry(self,master,description,var,sticky)-> ctk.CTkFrame:
        new_frame = ctk.CTkFrame(master, fg_color="transparent")
        row = 0
        if(description):
            self.create_normal_label(new_frame,description,TEXTSIZE.TEXT_X_SM,row,0,grid_args={"padx":WIDGET.PAD_X.value})
            row = row + 1
        CTkDateEntry(new_frame,variable=var,height=WIDGET.HEIGHT.value).grid(row=row, column=0, padx=WIDGET.PAD_X.value,sticky=sticky)
        return new_frame
        
    def create_normal_label(self,
                            master,
                            text: str,
                            size: TEXTSIZE,
                            row: int,
                            col: int,
                            label_args: dict | None = None,
                            grid_args: dict | None = None) -> ctk.CTkLabel:
        label_args = label_args or {}
        grid_args = grid_args or {}
        label = ctk.CTkLabel(master,text=text, font=self.font(size.value),**label_args)
        label.grid(row=row, column=col, **grid_args)
        return label
    
    def create_hyperlink_label(master,
                               text: str,
                               size: TEXTSIZE,
                               row: int,
                               col: int ):
        return

    def font(self, size : int, **args):
        return ctk.CTkFont(family="Arial",size=size, **args)
    

        
        


