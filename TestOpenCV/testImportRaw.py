import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
import cv2


def open_raw_file(filename, image_type, width, height, offset, num_images, gap, white_is_zero, little_endian,
                  open_all_files, use_virtual_stack):
    dtype_map = {
        '8-bit': np.uint8,
        '16-bit Signed': np.int16,
        '16-bit Unsigned': np.uint16,
        '32-bit Signed': np.int32,
        '32-bit Unsigned': np.uint32,
        '32-bit Real': np.float32,
        '64-bit Real': np.float64,
        '24-bit RGB': np.uint8  # Special handling needed for RGB
    }

    dtype = dtype_map[image_type]

    with open(filename, 'rb') as file:
        file.seek(offset)
        if image_type == '24-bit RGB':
            img = np.fromfile(file, dtype=dtype, count=width * height * 3).reshape((height, width, 3))
        else:
            img = np.fromfile(file, dtype=dtype, count=width * height).reshape((height, width))

    return img


def open_file_dialog():
    filename = filedialog.askopenfilename(title="Select RAW file",
                                          filetypes=[("RAW files", "*.raw"), ("All files", "*.*")])
    if filename:
        open_settings_dialog(filename)


def open_settings_dialog(filename):
    settings_dialog = tk.Toplevel()
    settings_dialog.title("Import RAW...")

    tk.Label(settings_dialog, text="Image type:").grid(row=0, column=0, sticky="e")
    image_type_var = tk.StringVar()
    image_type_combobox = ttk.Combobox(settings_dialog, textvariable=image_type_var)
    image_type_combobox['values'] = ('8-bit', '16-bit Signed', '16-bit Unsigned', '32-bit Signed',
                                     '32-bit Unsigned', '32-bit Real', '64-bit Real', '24-bit RGB')
    image_type_combobox.current(0)
    image_type_combobox.grid(row=0, column=1)

    tk.Label(settings_dialog, text="Width:").grid(row=1, column=0, sticky="e")
    width_entry = tk.Entry(settings_dialog)
    width_entry.grid(row=1, column=1)
    width_entry.insert(0, "720")

    tk.Label(settings_dialog, text="Height:").grid(row=2, column=0, sticky="e")
    height_entry = tk.Entry(settings_dialog)
    height_entry.grid(row=2, column=1)
    height_entry.insert(0, "576")

    tk.Label(settings_dialog, text="Offset to first image:").grid(row=3, column=0, sticky="e")
    offset_entry = tk.Entry(settings_dialog)
    offset_entry.grid(row=3, column=1)
    offset_entry.insert(0, "0")

    tk.Label(settings_dialog, text="Number of images:").grid(row=4, column=0, sticky="e")
    num_images_entry = tk.Entry(settings_dialog)
    num_images_entry.grid(row=4, column=1)
    num_images_entry.insert(0, "1")

    tk.Label(settings_dialog, text="Gap between images:").grid(row=5, column=0, sticky="e")
    gap_entry = tk.Entry(settings_dialog)
    gap_entry.grid(row=5, column=1)
    gap_entry.insert(0, "0")

    white_is_zero_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="White is zero", variable=white_is_zero_var).grid(row=6, column=0, sticky="w",
                                                                                           columnspan=2)

    little_endian_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="Little-endian byte order", variable=little_endian_var).grid(row=7, column=0,
                                                                                                      sticky="w",
                                                                                                      columnspan=2)

    open_all_files_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="Open all files in folder", variable=open_all_files_var).grid(row=8, column=0,
                                                                                                       sticky="w",
                                                                                                       columnspan=2)

    use_virtual_stack_var = tk.BooleanVar()
    tk.Checkbutton(settings_dialog, text="Use virtual stack", variable=use_virtual_stack_var).grid(row=9, column=0,
                                                                                                   sticky="w",
                                                                                                   columnspan=2)

    def on_ok():
        try:
            image_type = image_type_var.get()
            width = int(width_entry.get())
            height = int(height_entry.get())
            offset = int(offset_entry.get())
            num_images = int(num_images_entry.get())
            gap = int(gap_entry.get())
            white_is_zero = white_is_zero_var.get()
            little_endian = little_endian_var.get()
            open_all_files = open_all_files_var.get()
            use_virtual_stack = use_virtual_stack_var.get()

            img = open_raw_file(filename, image_type, width, height, offset, num_images, gap, white_is_zero,
                                little_endian, open_all_files, use_virtual_stack)
            cv2.imshow("RAW Image", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            settings_dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    tk.Button(settings_dialog, text="OK", command=on_ok).grid(row=10, column=0, sticky="e")
    tk.Button(settings_dialog, text="Cancel", command=settings_dialog.destroy).grid(row=10, column=1, sticky="w")


root = tk.Tk()
root.withdraw()

open_file_dialog()
root.mainloop()
