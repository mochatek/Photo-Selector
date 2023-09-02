import os
from tkinter import Tk, Frame, Button, Label, Listbox, Scrollbar, SINGLE, END
from tkinter import filedialog
from PIL import Image, ImageTk


MIN_ZOOM = 0.5
INIT_ZOOM = 1.0
MAX_ZOOM = 2.5
BG_COLOR = "#D3D3D3"


class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")
        self.image_paths = []
        self.current_index = 0
        self.selected_images = {}
        self.image_zoom = INIT_ZOOM

        side_panel = Frame(root)
        side_panel.pack(side="left", fill="y", padx=5, pady=5)

        load_button = Button(side_panel, text="Browse", command=self.load_folder)
        load_button.pack(side="top", fill="x")

        self.image_listbox = Listbox(side_panel, selectmode=SINGLE)
        self.image_listbox.pack(side="left", fill="both", expand=True, pady=5)

        listbox_scrollbar = Scrollbar(side_panel, command=self.image_listbox.yview)
        listbox_scrollbar.pack(side="right", fill="y")
        self.image_listbox.config(yscrollcommand=listbox_scrollbar.set)

        image_frame = Frame(
            root,
            width=self.root.winfo_screenwidth(),
            height=self.root.winfo_screenheight() - 125,
            bg=BG_COLOR,
        )
        image_frame.pack(padx=10, pady=5)

        self.image_label = Label(image_frame)
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        button_frame = Frame(root)
        button_frame.pack(side="bottom", pady=10)

        prev_button = Button(button_frame, text="Previous", command=self.prev_image)
        prev_button.pack(side="left", padx=5)

        self.select_button = Button(
            button_frame, text="Select", command=self.toggle_select_image
        )
        self.select_button.pack(side="left", padx=5)

        next_button = Button(button_frame, text="Next", command=self.next_image)
        next_button.pack(side="left", padx=5)

        zoom_in_button = Button(button_frame, text="➕", command=self.zoom_in)
        zoom_in_button.pack(side="left", padx=5)

        zoom_out_button = Button(button_frame, text="➖", command=self.zoom_out)
        zoom_out_button.pack(side="left", padx=5)

        # Maximize window
        self.root.state("zoomed")

        self.image_label.bind("<MouseWheel>", self.on_mousewheel)
        self.image_listbox.bind("<<ListboxSelect>>", self.show_selected_image)

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths = [
                os.path.join(folder_path, filename)
                for filename in os.listdir(folder_path)
                if filename.endswith((".jpg", ".png", ".jpeg"))
            ]
            self.current_index = 0
            self.image_zoom = INIT_ZOOM
            self.selected_images.clear()
            self.update_image_listbox()
            self.show_image()

    def show_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_index]
            image = Image.open(image_path)
            image = image.resize(
                (
                    int(image.width * self.image_zoom),
                    int(image.height * self.image_zoom),
                )
            )
            image = ImageTk.PhotoImage(image=image)
            self.image_label.config(image=image)
            self.image_label.photo = image

            if self.current_index in self.selected_images:
                self.select_button.config(text="Deselect")
                self.image_label.config(
                    borderwidth=3, bd=2, relief="solid", highlightbackground="green"
                )
            else:
                self.select_button.config(text="Select")
                self.image_label.config(borderwidth=0, relief="flat")

    def prev_image(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.image_zoom = INIT_ZOOM
            self.show_image()

    def next_image(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.image_zoom = INIT_ZOOM
            self.show_image()

    def toggle_select_image(self):
        if self.image_paths:
            if self.current_index in self.selected_images:
                del self.selected_images[self.current_index]
            else:
                self.selected_images[self.current_index] = self.image_paths[
                    self.current_index
                ]
            self.update_image_listbox()
            self.show_image()

    def zoom_in(self):
        self.image_zoom = min(MAX_ZOOM, self.image_zoom * 1.2)
        self.show_image()

    def zoom_out(self):
        self.image_zoom = max(self.image_zoom / 1.2, MIN_ZOOM)
        self.show_image()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

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
            self.image_zoom = INIT_ZOOM
            self.show_image()


if __name__ == "__main__":
    root = Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
