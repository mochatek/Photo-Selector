import os
from tkinter import Frame, Button, Label, Tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector")
        self.image_paths = []
        self.current_index = 0
        self.selected_images = {}
        self.image_zoom = 1.0

        self.load_button = Button(root, text="Browse", command=self.load_folder)
        self.load_button.pack(pady=10)

        image_frame = Frame(root, width=self.root.winfo_screenwidth(), height=600)
        image_frame.pack(padx=10, pady=5)

        self.image_label = Label(image_frame)
        self.image_label.place(relx=0.5, rely=0.5, anchor='center')

        button_frame = Frame(root)
        button_frame.pack(side='bottom', pady=10)

        self.prev_button = Button(button_frame, text="Previous", command=self.prev_image)
        self.prev_button.pack(side='left', padx=5)

        self.select_button = Button(button_frame, text="Select", command=self.toggle_select_image)
        self.select_button.pack(side='left', padx=5)

        self.next_button = Button(button_frame, text="Next", command=self.next_image)
        self.next_button.pack(side='left', padx=5)

        self.zoom_in_button = Button(button_frame, text="➕", command=self.zoom_in)
        self.zoom_in_button.pack(side='left', padx=5)

        self.zoom_out_button = Button(button_frame, text="➖", command=self.zoom_out)
        self.zoom_out_button.pack(side='left', padx=5)

        # Maximize window 
        self.root.state('zoomed')

        self.image_label.bind('<MouseWheel>', self.on_mousewheel)


    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith((".jpg", ".png", ".jpeg"))]
            self.current_index = 0
            self.show_image()

    def show_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_index]
            image = Image.open(image_path)
            image = image.resize((int(image.width * self.image_zoom), int(image.height * self.image_zoom)))
            photo = ImageTk.PhotoImage(image=image)
            self.image_label.config(image=photo)
            self.image_label.photo = photo

            if self.current_index in self.selected_images:
                self.select_button.config(text="Deselect")
                self.image_label.config(borderwidth=3, bd=2, relief="solid", highlightbackground="green")
            else:
                self.select_button.config(text="Select")
                self.image_label.config(borderwidth=0, relief="flat")

    def prev_image(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.show_image()

    def next_image(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.show_image()

    def toggle_select_image(self):
        if self.image_paths:
            if self.current_index in self.selected_images:
                del self.selected_images[self.current_index]
            else:
                self.selected_images[self.current_index] = self.image_paths[self.current_index]
            
            self.show_image()

    def zoom_in(self):
        self.image_zoom = min(2.5, self.image_zoom * 1.2)
        self.show_image()

    def zoom_out(self):
        self.image_zoom = max(self.image_zoom / 1.2, 0.5)
        self.show_image()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    

if __name__ == "__main__":
    root = Tk()
    app = ImageSelectorApp(root)
    root.mainloop()