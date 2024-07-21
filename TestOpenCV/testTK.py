import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageStat
import numpy as np

class ImageJClone(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('ImageJ Clone')

        # Menu bar
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_image)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

        # Canvas for image display
        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<ButtonPress-3>", self.show_context_menu)

        # Variables to store image and selection
        self.image = None
        self.tk_image = None
        self.rect = None
        self.start_x = self.start_y = 0

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("RAW files", "*.raw"), ("All files", "*.*")])
        if file_path:
            self.load_raw_image(file_path, (576, 720))

    def load_raw_image(self, file_path, shape):
        # Load raw image file
        image_data = np.fromfile(file_path, dtype=np.uint8)
        image_data = image_data.reshape(shape)
        self.image = Image.fromarray(image_data)

        # Convert image to Tkinter format and display
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        pass

    def show_context_menu(self, event):
        if self.rect:
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="ROW Properties", command=self.show_row_properties_dialog)
            menu.add_command(label="Measure", command=self.measure_area)
            menu.post(event.x_root, event.y_root)

    def show_row_properties_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("ROW Properties")

        labels = ["Property 1", "Property 2", "Property 3", "Property 4", "Property 5"]
        self.inputs = []

        for label in labels:
            frame = tk.Frame(dialog)
            frame.pack(fill=tk.X, padx=5, pady=5)
            tk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
            input_field = tk.Entry(frame)
            input_field.pack(fill=tk.X, expand=True)
            self.inputs.append(input_field)

        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(button_frame, text="OK", command=dialog.destroy).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def measure_area(self):
        if not self.image or not self.rect:
            return

        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        cropped = self.image.crop((x1, y1, x2, y2))
        stat = ImageStat.Stat(cropped)

        area = (x2 - x1) * (y2 - y1)
        mean_val = stat.mean[0]
        min_val = stat.extrema[0][0]
        max_val = stat.extrema[0][1]

        messagebox.showinfo("Measure", f"Area: {area}\nMean: {mean_val}\nMin: {min_val}\nMax: {max_val}")

if __name__ == '__main__':
    app = ImageJClone()
    app.geometry("800x600")
    app.mainloop()
