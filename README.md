# TkTable
A Tk Widget to display and edit a DataFrame
![Screenshot of a simple table displayed in TkTable](https://github.com/matthewmisiaszek/TkTable/blob/main/demo.png)  
TkTable is a subclass of Tkinter Frame and utilizes Tkinter Treeview to display the table.

## Running
Import `import TkTable as tkt`  
Create a TkTable Widget `TkTable(parent, DataFrame, buttons, custom_buttons)`  
- parent: a Tk widget or window  
- DataFrame: a pandas DataFrame  
- buttons (optional): a tuple of editing buttons to include (see docstring), default is none  
  - Allowed Buttons:  
    - tkt.APPEND_ROW
    - tkt.INSERT_ROW
    - tkt.MOVE_ROW
    - tkt.DELETE_ROW
    - tkt.EDIT_ROW
    - tkt.APPEND_COLUMN
    - tkt.MOVE_COLUMN
    - tkt.DELETE_COLUMN
    - tkt.SET_INDEX
    - tkt.REFRESH
  - Pre-defined button groups:
    - tkt.VIEW_ONLY
    - tkt.ROW_ONLY
    - tkt.COLUMN_ONLY
    - tkt.ALL
    - tkt.NONE  
- custom_buttons (optional): a tuple of (label, command) pairs to add more buttons, default is none  

Returns a TkTable widget    
Pack or grid the widget like any other: `table.pack(side='top', expand=True, fill='both')`  
Refresh the DataFrame view after an external change: `table.refresh()`  
Append a row to the DataFrame: `table.append_row(values)` where values is a list in the same order as the index and columns of the DataFrame  
Insert a row into the DataFrame: `table.insert_row(idx, values)` where idx is the integer index of the row to insert above  

If you run the file by itself (`python TkTable.py`) a demo .csv editor function will run.
