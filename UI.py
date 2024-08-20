import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
# from outline_features import main_function

from outline_features_backup import main_function
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotly.offline as pyo
import webbrowser
import os
from cefpython3 import cefpython as cef
import platform
import sys


class UserInterface:
    def __init__(self, master):
        self.master = master
        master.title("POC")

        # Fullscreen
        master.state('zoomed')

        # Configure the master background color
        master.configure(bg='lightblue')

        # Create custom font
        custom_font = ("Helvetica", 14)

        # Create widgets with customization
        self.file1_label = tk.Label(master, text="受注:", font=custom_font, bg='lightblue', fg='black')
        self.file1_entry = tk.Entry(master, width=50)
        self.file1_button = tk.Button(master, text="Browse", command=self.browse_file1, width=10, bg='steelblue', fg='white', activebackground='dodgerblue', relief=tk.RAISED)

        self.file2_label = tk.Label(master, text="受注_reorder:", font=custom_font, bg='lightblue', fg='black')
        self.file2_entry = tk.Entry(master, width=50)
        self.file2_button = tk.Button(master, text="Browse", command=self.browse_file2, width=10, bg='steelblue', fg='white', activebackground='dodgerblue', relief=tk.RAISED)

        self.start_label = tk.Label(master, text="開始日 (MM/DD/YYYY):", font=custom_font, bg='lightblue', fg='black')
        self.start_entry = tk.Entry(master, width=50)

        self.end_label = tk.Label(master, text="最終日 (MM/DD/YYYY):", font=custom_font, bg='lightblue', fg='black')
        self.end_entry = tk.Entry(master, width=50)

        self.holiday_label = tk.Label(master, text="休日範囲:", font=custom_font, bg='lightblue', fg='black')
        self.holiday_from_label = tk.Label(master, text="休日開始日 (MM/DD/YYYY):", font=custom_font, bg='lightblue', fg='black')
        self.holiday_from_entry = tk.Entry(master, width=50)
        self.holiday_to_label = tk.Label(master, text="休日終了日 (MM/DD/YYYY):", font=custom_font, bg='lightblue', fg='black')
        self.holiday_to_entry = tk.Entry(master, width=50)

        self.submit_button = tk.Button(master, text="Submit", command=self.submit, width=20, bg='steelblue', fg='white', activebackground='dodgerblue', relief=tk.RAISED)

        # Layout
        self.file1_label.grid(row=0, column=0, sticky='e', padx=(20, 10), pady=(20, 10))
        self.file1_entry.grid(row=0, column=1, padx=(0, 10), pady=(20, 10))
        self.file1_button.grid(row=0, column=2, padx=(0, 20), pady=(20, 10))

        self.file2_label.grid(row=1, column=0, sticky='e', padx=(20, 10), pady=(10, 10))
        self.file2_entry.grid(row=1, column=1, padx=(0, 10), pady=(10, 10))
        self.file2_button.grid(row=1, column=2, padx=(0, 20), pady=(10, 10))

        self.start_label.grid(row=2, column=0, sticky='e', padx=(20, 10), pady=(10, 10))
        self.start_entry.grid(row=2, column=1, padx=(0, 10), pady=(10, 10))

        self.end_label.grid(row=3, column=0, sticky='e', padx=(20, 10), pady=(10, 10))
        self.end_entry.grid(row=3, column=1, padx=(0, 10), pady=(10, 10))

        self.holiday_label.grid(row=4, column=0, sticky='e', padx=(20, 10), pady=(10, 10))
        self.holiday_from_label.grid(row=5, column=0, sticky='e', padx=(20, 10), pady=(10, 10))
        self.holiday_from_entry.grid(row=5, column=1, padx=(0, 10), pady=(10, 10))
        self.holiday_to_label.grid(row=6, column=0, sticky='e', padx=(20, 10), pady=(10, 10))
        self.holiday_to_entry.grid(row=6, column=1, padx=(0, 10), pady=(10, 10))

        self.submit_button.grid(row=7, column=1, padx=(0, 10), pady=(10, 20))

    def browse_file1(self):
        self.file1_entry.delete(0, tk.END)
        self.file1_entry.insert(0, filedialog.askopenfilename())

    def browse_file2(self):
        self.file2_entry.delete(0, tk.END)
        self.file2_entry.insert(0, filedialog.askopenfilename())

    def submit(self):
        file1 = self.file1_entry.get()
        file2 = self.file2_entry.get()
        start = self.start_entry.get()
        end = self.end_entry.get()
        holiday_from = self.holiday_from_entry.get()
        holiday_to = self.holiday_to_entry.get()

        # Validation
        if not file1 or not file2 or not start or not end:
            messagebox.showerror("Error", "All fields except holiday ranges must be filled.")
            return

        main_function(file1, file2, start, end, holiday_from, holiday_to)

        # try:
        #     # Call your main function with the parameters
        #     main_function(file1, file2, start, end, holiday_from, holiday_to)
        #     messagebox.showinfo("Success", "Processing complete!")
        # except Exception as e:
        #     messagebox.showerror("Error", f"An error occurred: {str(e)}")

root = tk.Tk()
ui = UserInterface(root)
root.mainloop()
