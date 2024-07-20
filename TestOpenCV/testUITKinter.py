import tkinter as tk
from tkinter import filedialog, Menu, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageJClone(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ImageJ Clone")
        self.geometry("800x600")

        self.image_path = None
        self.original_image = None
        self.display_image = None

        self.create_menu()
        self.create_canvas()

    def create_menu(self):
        menu_bar = Menu(self)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Rotate", command=self.rotate_image)
        edit_menu.add_command(label="Resize", command=self.resize_image)
        edit_menu.add_command(label="Blur", command=self.blur_image)
        edit_menu.add_command(label="Edge Detection", command=self.edge_detection)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

    def create_canvas(self):
        self.canvas = tk.Canvas(self, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            self.display_image = self.original_image.copy()
            self.show_image(self.display_image)

    def save_image(self):
        if self.display_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if file_path:
                cv2.imwrite(file_path, self.display_image)
        else:
            messagebox.showerror("Error", "No image to save")

    def show_image(self, image):
        bgr_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(bgr_image)
        imgtk = ImageTk.PhotoImage(image=pil_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.canvas.image = imgtk

    def rotate_image(self):
        if self.display_image is not None:
            angle = 90  # Here, you can add a dialog to ask for the angle
            (h, w) = self.display_image.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            self.display_image = cv2.warpAffine(self.display_image, matrix, (w, h))
            self.show_image(self.display_image)
        else:
            messagebox.showerror("Error", "No image to rotate")

    def resize_image(self):
        if self.display_image is not None:
            width = 200  # Here, you can add a dialog to ask for the new width
            height = 200  # Here, you can add a dialog to ask for the new height
            self.display_image = cv2.resize(self.display_image, (width, height))
            self.show_image(self.display_image)
        else:
            messagebox.showerror("Error", "No image to resize")

    def blur_image(self):
        if self.display_image is not None:
            ksize = 5  # Here, you can add a dialog to ask for the kernel size
            self.display_image = cv2.GaussianBlur(self.display_image, (ksize, ksize), 0)
            self.show_image(self.display_image)
        else:
            messagebox.showerror("Error", "No image to blur")

    def edge_detection(self):
        if self.display_image is not None:
            self.display_image = cv2.Canny(self.display_image, 100, 200)
            self.show_image(self.display_image)
        else:
            messagebox.showerror("Error", "No image for edge detection")

    def show_about(self):
        messagebox.showinfo("About", "ImageJ Clone\nCreated with Python and Tkinter")

if __name__ == "__main__":
    app = ImageJClone()
    app.mainloop()
