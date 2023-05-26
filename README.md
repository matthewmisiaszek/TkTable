# TkTable
A Tk Widget to display and edit a DataFrame

## Running
Import `from TkTable import TkTable`  
If you run the file by itself (`python TkTable.py`) a demo function will run and create a Tk Window from a user-selected .csv file.

Create a TkTable Widget `TkTable(parent, DataFrame, buttons, custom_buttons)`  
parent: a Tk widget or window  
DataFrame: a pandas DataFrame  
buttons (optional): a tuple of editing buttons to include (see docstring), default is none  
custom_buttons (optional): a tuple of (label, command) pairs to add more buttons, default is none  
Returns a TkTable object  
TkTable is a subclass of Tkinter Frame
