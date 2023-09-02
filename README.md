# Photo$ - Photo Selector
A Tkinter application to select photos from a folder and copy them to another folder

## Features
- View photos from a folder
- Supports slideshow
- Supports zoom-in and zoom-out
- Select/deselect images that we like to copy
- View selections
- Export selection as JSON file
- Copy selected files directly to a destination folder
- Copy selection from an imported JSON file

## Shortcuts
- Slideshow - `Arrow keys`
- Zooming - `Mousewheel`
- Select/Deselect - `Enter key`

## Packaging
```
pyinstaller --onefile --icon=app.ico --name=Photo$ --noconsole --add-data "app.ico;."  main.py
```
