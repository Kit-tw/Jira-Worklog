import customtkinter as ctk
from customtkinter import filedialog
class GoogleApiPage(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent)
        self.input_frame()
    

    def input_frame(self):
        select_file_btn = ctk.CTkButton(self,text="Choose File",command=self.select_file)
        select_file_btn.grid()

    def select_file(self):
        filename = filedialog.askopenfilename()
        print(filename)

    