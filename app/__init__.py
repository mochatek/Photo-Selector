from tkinter import (
    Tk,
    Frame,
    Button,
    Label,
    Listbox,
    Scrollbar,
    Toplevel,
    Entry,
    messagebox,
    DoubleVar,
    SINGLE,
    END,
)
from tkinter.ttk import Notebook, Frame as TFrame, Button as TButton, Progressbar
from tkinter import filedialog
from PIL import Image, ImageTk
from os import listdir
from os.path import exists, join, basename, dirname
from json import dump, load
from shutil import copyfile
from threading import Thread, Event
from .zoom import Zoomscale

# Show app icon in taskbar
try:
    from ctypes import windll

    myappid = "Mochatek.Photo$.v1.0"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

FONT = "Segoe UI Emoji"
APP_FONT_SIZE = 12
POPUP_FONT_SIZE = 10
ENTRY_FONT_SIZE = 9
MIN_ZOOM = -2
MAX_ZOOM = 4
ZOOM_FACTOR = 1.2
BG_COLOR = "#D3D3D3"
ELEM_GAP = 5
WINDOW_GAP = 10
SUPPORTED_IMG_FORMATS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".ppm",
    ".pgm",
    ".pbm",
    ".tif",
    ".tiff",
    ".ico",
)


class ImageSelectorApp:
    def __init__(self, root: Tk, icon_path: str):
        self.image_paths = []
        self.current_index = 0
        self.selected_images = {}
        self.zoom_level = Zoomscale(MIN_ZOOM, MAX_ZOOM)
        self.image_zoom = 0
        self.image_angle = 0
        self.image: Image = None
        self.image_contain_width, self.image_contain_height = 0, 0

        root.title("Photo$ © MochaTek ‣ 2023")
        root.state("zoomed")
        root.iconbitmap(icon_path)
        root.option_add("*font", (FONT, APP_FONT_SIZE))

        side_panel = Frame(root)
        side_panel.pack(side="left", fill="y", padx=WINDOW_GAP, pady=WINDOW_GAP)

        button_frame = Frame(side_panel)
        button_frame.pack(side="top", fill="x")

        load_button = Button(button_frame, text="📁 Browse", command=self.load_folder)
        load_button.pack(side="left", padx=ELEM_GAP)

        export_button = Button(
            button_frame,
            text="💾 Export",
            command=lambda: self.open_export_popup(
                root, list(self.selected_images.values())
            ),
        )
        export_button.pack(side="left", padx=ELEM_GAP)

        self.image_listbox = Listbox(side_panel, selectmode=SINGLE)
        self.image_listbox.pack(
            side="left", fill="both", expand=True, pady=(ELEM_GAP, 0)
        )

        listbox_scrollbar = Scrollbar(side_panel, command=self.image_listbox.yview)
        listbox_scrollbar.pack(side="right", fill="y")
        self.image_listbox.config(yscrollcommand=listbox_scrollbar.set)

        controls_frame = Frame(root)
        controls_frame.pack(
            side="bottom", padx=(0, WINDOW_GAP), pady=(ELEM_GAP, WINDOW_GAP)
        )

        prev_button = Button(controls_frame, text="⬅️", command=self.prev_image)
        prev_button.pack(side="left", padx=ELEM_GAP)

        next_button = Button(controls_frame, text="➡️", command=self.next_image)
        next_button.pack(side="left", padx=ELEM_GAP)

        self.select_button = Button(
            controls_frame, text="✔️", command=self.toggle_select_image
        )
        self.select_button.pack(side="left", padx=ELEM_GAP)

        zoom_in_button = Button(controls_frame, text="➕", command=self.zoom_in)
        zoom_in_button.pack(side="left", padx=ELEM_GAP)

        zoom_out_button = Button(controls_frame, text="➖", command=self.zoom_out)
        zoom_out_button.pack(side="left", padx=ELEM_GAP)

        rotate_button = Button(controls_frame, text="📐", command=self.rotate_image)
        rotate_button.pack(side="left", padx=ELEM_GAP)

        self.filename_entry = Entry(
            controls_frame, width=30, relief="sunken", font=(FONT, ENTRY_FONT_SIZE)
        )
        self.filename_entry.pack(side="left", padx=ELEM_GAP)

        find_button = Button(
            controls_frame,
            text="🔍",
            font=(FONT, ENTRY_FONT_SIZE),
            command=self.find_image,
        )
        find_button.pack(side="left")

        (
            self.image_contain_width,
            self.image_contain_height,
        ) = root.winfo_screenwidth() - (
            side_panel.winfo_width() + (2 * WINDOW_GAP) + ELEM_GAP
        ), root.winfo_screenheight() - (
            controls_frame.winfo_height() + (2 * WINDOW_GAP) + ELEM_GAP
        )
        image_frame = Frame(
            root,
            width=self.image_contain_width,
            height=self.image_contain_height,
            bg=BG_COLOR,
        )
        image_frame.pack(padx=(0, WINDOW_GAP), pady=(WINDOW_GAP, 0))

        self.image_label = Label(image_frame)
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        self.image_label.bind("<MouseWheel>", self.zoom_image)
        self.image_listbox.bind("<<ListboxSelect>>", self.show_selected_image)

        root.bind("<Left>", self.prev_image)
        root.bind("<Right>", self.next_image)
        root.bind("<Return>", self.toggle_select_image)
        root.bind("<Control-r>", self.rotate_image)

    def __resize_image(self, image: Image = None):
        transformed_image = image or self.image
        # Scale image to best fit on initial load
        if self.zoom_level.at_base:
            scale_x = self.image_contain_width / transformed_image.width
            scale_y = self.image_contain_height / transformed_image.height
            self.image_zoom = min(scale_x, scale_y)

        return transformed_image.resize(
            (
                int(transformed_image.width * self.image_zoom),
                int(transformed_image.height * self.image_zoom),
            )
        )

    def __rotate_image(self, image: Image = None):
        transformed_image = image or self.image
        return transformed_image.rotate(self.image_angle, expand=True)

    def __display_image(self, transformed_image: Image):
        image = ImageTk.PhotoImage(image=transformed_image)
        self.image_label.config(image=image)
        self.image_label.image = image

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths = [
                join(folder_path, filename)
                for filename in listdir(folder_path)
                if filename.lower().endswith(SUPPORTED_IMG_FORMATS)
            ]
            self.current_index = 0
            self.selected_images.clear()
            self.update_image_listbox()
            self.filename_entry.delete(0, END)
            self.load_image()

    def load_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_index]
            self.filename_entry.delete(0, END)
            self.filename_entry.insert(0, basename(image_path))
            self.image = Image.open(image_path)
            self.image_angle = 0
            self.zoom_level.reset()
            self.__display_image(self.__resize_image())

            if self.current_index in self.selected_images:
                self.select_button.config(text="❌")
                self.image_label.config(
                    borderwidth=3, bd=2, relief="solid", highlightbackground="green"
                )
            else:
                self.select_button.config(text="✔️")
                self.image_label.config(borderwidth=0, relief="flat")

    def prev_image(self, event=None):
        if event and event.widget == self.filename_entry:
            return

        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.load_image()

    def next_image(self, event=None):
        if event and event.widget == self.filename_entry:
            return

        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.load_image()

    def toggle_select_image(self, event=None):
        if event and event.widget == self.filename_entry:
            return

        if self.image_paths:
            if self.current_index in self.selected_images:
                del self.selected_images[self.current_index]
            else:
                self.selected_images[self.current_index] = self.image_paths[
                    self.current_index
                ]
            self.update_image_listbox()
            self.load_image()

    def zoom_in(self):
        if self.image:
            self.zoom_level.up()
            if self.zoom_level.has_changed:
                self.image_zoom *= ZOOM_FACTOR
                self.__display_image(self.__resize_image(self.__rotate_image()))

    def zoom_out(self):
        if self.image:
            self.zoom_level.down()
            if self.zoom_level.has_changed:
                self.image_zoom /= ZOOM_FACTOR
                self.__display_image(self.__resize_image(self.__rotate_image()))

    def rotate_image(self, event=None):
        if self.image:
            self.image_angle = (self.image_angle - 90) % 360
            self.__display_image(self.__resize_image(self.__rotate_image()))

    def zoom_image(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def find_image(self):
        self.image_label.focus_set()

        filename = self.filename_entry.get()
        if self.image_paths:
            folder_path = dirname(self.image_paths[self.current_index])
            file_path = join(folder_path, filename)
            found_index = next(
                (
                    index
                    for index, path in enumerate(self.image_paths)
                    if path.lower() == file_path.lower()
                ),
                None,
            )
            if found_index is not None:
                self.current_index = found_index
                self.load_image()

    def update_image_listbox(self):
        self.image_listbox.delete(0, END)
        for index, image_index in enumerate(self.selected_images.keys()):
            image_name = self.selected_images[image_index].rsplit("\\", 1)[-1]
            self.image_listbox.insert(index, image_name)

    def show_selected_image(self, event):
        selected_index = self.image_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            image_index = list(self.selected_images.keys())[selected_index]
            self.current_index = image_index
            self.load_image()

    def open_export_popup(self, root: Tk, selected_files: list):
        export_window = Toplevel(root)
        export_window.title("Export")
        export_window.transient(root)  # Stack popup on top of main
        export_window.grab_set()  # Disable access to main
        export_window.option_add("*font", (FONT, POPUP_FONT_SIZE))

        # Centralize popup window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = (screen_width - export_window.winfo_reqwidth()) // 3
        center_y = (screen_height - export_window.winfo_reqheight()) // 2
        export_window.geometry(f"+{center_x}+{center_y}")

        tab_control = Notebook(export_window)
        save_tab = TFrame(tab_control)
        copy_tab = TFrame(tab_control)
        tab_control.add(save_tab, text="Save selection as JSON")
        tab_control.add(copy_tab, text="Copy selected files")
        tab_control.pack(fill="both", expand=True)

        def browse_jsonfile(entry: Entry):
            json_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
            if json_file:
                entry.delete(0, END)
                entry.insert(0, json_file)

        def browse_destination(entry: Entry):
            folder = filedialog.askdirectory()
            if folder:
                entry.delete(0, END)
                entry.insert(0, folder)

        def export_to_json(entry: Entry):
            json_path = entry.get()
            if not exists(json_path):
                messagebox.showerror("Error", "Please select a valid path.")
                return

            try:
                with open(join(json_path, "selection.json"), "w") as json_file:
                    dump(selected_files, json_file)
            except Exception as e:
                messagebox.showerror("Error", str(e))
            else:
                messagebox.showinfo("Success", "Selection saved as JSON.")

        def copy_files(
            files: list, target_folder: str, progress: DoubleVar, stop_event: Event
        ):
            total_files = len(files)
            copied_files = 0

            for source_file in files:
                if stop_event.is_set():
                    return

                try:
                    file_name = basename(source_file)
                    target_file = join(target_folder, file_name)
                    copyfile(source_file, target_file)
                except:
                    pass
                copied_files += 1
                progress.set(100.0 * copied_files / total_files)
                export_window.update()
            messagebox.showinfo("Success", "Files copied successfully.")

        def copy_selected_files(
            sourceEntry: Entry,
            targetEntry: Entry,
            progress_bar: Progressbar,
            progress: DoubleVar,
        ):
            __selected_files = selected_files
            source_json_path = sourceEntry.get()
            target_folder = targetEntry.get()

            if not exists(target_folder):
                messagebox.showerror("Error", "Please select a valid destination path.")
                return

            if source_json_path:
                if not exists(source_json_path):
                    messagebox.showerror("Error", "Please select a valid JSON file.")
                    return
                try:
                    with open(source_json_path, "r") as json_file:
                        __selected_files = load(json_file)
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    return

            stop_event = Event()
            copy_thread = Thread(
                target=copy_files,
                args=(__selected_files, target_folder, progress, stop_event),
            )
            copy_thread.start()

            progress_bar.grid(
                row=2,
                column=0,
                columnspan=3,
                padx=WINDOW_GAP,
                pady=WINDOW_GAP,
                sticky="ew",
            )

            def on_closing():
                if copy_thread.is_alive():
                    stop_event.set()
                    copy_thread.join()
                export_window.destroy()

            export_window.protocol("WM_DELETE_WINDOW", on_closing)

        Label(save_tab, text="Select Target Folder:").grid(
            row=1, column=0, padx=WINDOW_GAP, pady=WINDOW_GAP
        )
        save_json_entry = Entry(save_tab, width=40)
        save_json_entry.grid(row=1, column=1, padx=WINDOW_GAP, pady=WINDOW_GAP)
        save_json_browse_button = TButton(
            save_tab,
            text="Browse",
            command=lambda: browse_destination(save_json_entry),
        )
        save_json_browse_button.grid(row=1, column=2, padx=WINDOW_GAP, pady=WINDOW_GAP)
        save_button = TButton(
            save_tab, text="Save", command=lambda: export_to_json(save_json_entry)
        )
        save_button.grid(row=2, column=0, columnspan=3, pady=WINDOW_GAP)

        Label(copy_tab, text="Select JSON File:").grid(
            row=0, column=0, padx=WINDOW_GAP, pady=WINDOW_GAP
        )
        copy_json_entry = Entry(copy_tab, width=40)
        copy_json_entry.grid(row=0, column=1, padx=WINDOW_GAP, pady=WINDOW_GAP)
        copy_json_browse_button = TButton(
            copy_tab, text="Browse", command=lambda: browse_jsonfile(copy_json_entry)
        )
        copy_json_browse_button.grid(row=0, column=2, padx=WINDOW_GAP, pady=WINDOW_GAP)

        Label(copy_tab, text="Select Destination Folder:").grid(
            row=1, column=0, padx=WINDOW_GAP, pady=WINDOW_GAP
        )
        copy_destination_entry = Entry(copy_tab, width=40)
        copy_destination_entry.grid(row=1, column=1, padx=WINDOW_GAP, pady=WINDOW_GAP)
        copy_destination_browse_button = TButton(
            copy_tab,
            text="Browse",
            command=lambda: browse_destination(copy_destination_entry),
        )
        copy_destination_browse_button.grid(
            row=1, column=2, padx=WINDOW_GAP, pady=WINDOW_GAP
        )
        progress_var = DoubleVar()
        progress_bar = Progressbar(copy_tab, variable=progress_var, maximum=100)
        copy_button = TButton(
            copy_tab,
            text="Copy",
            command=lambda: copy_selected_files(
                copy_json_entry, copy_destination_entry, progress_bar, progress_var
            ),
        )
        copy_button.grid(row=3, column=0, columnspan=3, pady=WINDOW_GAP)
