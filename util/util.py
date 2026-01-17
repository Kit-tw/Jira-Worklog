import os
import customtkinter
import webbrowser
import json

def find(name : str, path: str):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root,name)

def font(size : int):
    return customtkinter.CTkFont(family="Arial",size=size)


def opon_url(url):
    webbrowser.open(url)

def save_json_file(path: str, filename : str, data : object) -> None:
    try:
        for root, dirs, files in os.walk(path):
            with open(filename + ".json",'w') as file:
                json.dump(data,file)
    except:
        #TODO : change print to open dialog show error / tell error occure
        print("save_json_file exception occured")
        