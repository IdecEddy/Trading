#!/bin/python3
import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime

def close_window():
    root.destroy()

def get_selected_date():
    selected_date = cal1.get_date()
    selected_timestamp = datetime.strptime(selected_date, "%d/%m/%y").timestamp()
    selected_date_label1.config(text=f"Unix Timestamp: {int(selected_timestamp)}")

def get_selected_date2():
    selected_date = cal2.get_date()
    selected_date_label2.config(text=f"Selected Date 2: {selected_date}")

root = tk.Tk()
root.title("Window with Stylish Date Selection")

# Create a button for closing the window
close_button = tk.Button(root, text="Close", command=close_window)
close_button.pack(side=tk.TOP, anchor=tk.NE)

# Create a frame for the first calendar and related widgets
frame1 = tk.Frame(root)
frame1.pack(side=tk.LEFT, padx=10)

# Create the first calendar widget for date selection
cal1 = Calendar(frame1, height=200, width=200)
cal1.pack()

# Create a button to get the selected date from the first calendar
get_date_button1 = tk.Button(frame1, text="Get Selected Date 1", command=get_selected_date)
get_date_button1.pack()

# Create a label to display the selected date from the first calendar
selected_date_label1 = tk.Label(frame1, text="")
selected_date_label1.pack()

# Create a frame for the second calendar and related widgets
frame2 = tk.Frame(root)
frame2.pack(side=tk.LEFT, padx=10)

# Create the second calendar widget for date selection
cal2 = Calendar(frame2, height=200, width=200)
cal2.pack()

# Create a button to get the selected date from the second calendar
get_date_button2 = tk.Button(frame2, text="Get Selected Date 2", command=get_selected_date2)
get_date_button2.pack()

# Create a label to display the selected date from the second calendar
selected_date_label2 = tk.Label(frame2, text="")
selected_date_label2.pack()

root.mainloop()
