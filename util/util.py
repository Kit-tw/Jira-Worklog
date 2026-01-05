import os
import tkinter.font as tkFont

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root,name)

def font(size):
    return tkFont.Font(family="Arial",size=size)