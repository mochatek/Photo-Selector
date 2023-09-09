"""
    Photo$ - Photo Selector

    Description: A Tkinter application to select photos from a folder and copy them to another folder
    Developer  : Akash S Panickar (MochaTek)
    Year       : 2023
    Packaging  : pyinstaller --onefile --icon=app.ico --name=Photo$ --noconsole --add-data "app.ico;."  main.py
"""

from tkinter import Tk
from os.path import join, dirname
from app import ImageSelectorApp

if __name__ == "__main__":
    root = Tk()
    app_icon = join(dirname(__file__), "app.ico")
    app = ImageSelectorApp(root, app_icon)
    root.mainloop()
