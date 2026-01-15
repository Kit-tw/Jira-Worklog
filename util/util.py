import os
import customtkinter
import webbrowser
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root,name)

def font(size : int):
    return customtkinter.CTkFont(family="Arial",size=size)


def opon_url(url):
    webbrowser.open(url)