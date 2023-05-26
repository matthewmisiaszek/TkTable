"""A Tkinter Widget to display and edit a DataFrame"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import typing


# Constants
# Button labels and names
APPEND_ROW = 'Append Row'
INSERT_ROW = 'Insert Row'
MOVE_ROW = 'Move Row'
DELETE_ROW = 'Delete Row'
EDIT_ROW = 'Edit Row'
APPEND_COLUMN = 'Append Column'
MOVE_COLUMN = 'Move Column'
DELETE_COLUMN = 'Delete Column'
SET_INDEX = 'Set Index'
REFRESH = 'Refresh'

VIEW_ONLY = (
    REFRESH,
    )
ROW_ONLY = (
    APPEND_ROW,
    INSERT_ROW,
    MOVE_ROW,
    EDIT_ROW,
    DELETE_ROW,
    REFRESH
    )
COLUMN_ONLY = (
    APPEND_COLUMN,
    MOVE_COLUMN,
    DELETE_COLUMN,
    SET_INDEX,
    REFRESH
    )
ALL = (
    APPEND_ROW,
    INSERT_ROW,
    MOVE_ROW,
    EDIT_ROW,
    DELETE_ROW,
    APPEND_COLUMN,
    MOVE_COLUMN,
    DELETE_COLUMN,
    SET_INDEX,
    REFRESH
)
NONE = tuple()



class TkTable(tk.Frame):
    """A Tkinter Widget to display and edit a DataFrame

    DataFrame edits are done without reassigning the DataFrame
    variable, meaning that existing references to the DataFrame
    will continue to work.
    
    Valid buttons: APPEND_ROW, INSERT_ROW, MOVE_ROW, EDIT_ROW,
    DELETE_ROW, APPEND_COLUMN, MOVE_COLUMN, DELETE_COLUMN,
    SET_INDEX, REFRESH"""
    def __init__(self, parent:tk.Widget, df:pd.DataFrame, 
                 buttons:tuple[str,...]=VIEW_ONLY, 
                 custom_buttons:tuple[tuple[str, typing.Callable],...]=NONE):
        tk.Frame.__init__(self, parent)
        self.df = df
        tree_frame = tk.Frame(self)
        tree_frame.pack(side='top', expand=True, fill='both')
        self.tree = ttk.Treeview(tree_frame, show='headings')
        self.tree.pack(side='top', expand=True, fill='both')
        self.buttons_frame = None
        self.buttons = buttons
        self.custom_buttons = custom_buttons
        self.make_buttons()
        self.refresh()

    def make_buttons(self):
        if isinstance(self.buttons_frame, tk.Widget):
            self.buttons_frame.destroy()
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(side='top', fill='x')

        button_dict = {
        APPEND_ROW: self.append_row,
        INSERT_ROW: self.insert_row,
        MOVE_ROW: self.move_row,
        DELETE_ROW: self.delete_row,
        EDIT_ROW: self.edit_row,
        APPEND_COLUMN: self.add_column,
        MOVE_COLUMN: self.move_column,
        DELETE_COLUMN: self.delete_column,
        SET_INDEX: self.set_index,
        REFRESH: self.refresh
        }

        buttons = tuple((bn, button_dict[bn]) 
                        for bn in self.buttons
                        if bn in button_dict)
        for bn, bc in buttons + self.custom_buttons:
            tk.Button(self.buttons_frame, text=bn, 
                        command=bc).pack(side='left')
    
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree['columns'] = _get_df_head(self.df)
        for column in self.tree['columns']:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)
        for i in range(self.df.shape[0]):
            row = _get_df_row(self.df, i)
            self.tree.insert('', 'end', i, values=row)
    
    def append_row(self):
        new_row = self.row_editor()
        temp_df = pd.concat([self.df, new_row], copy=False, ignore_index=False)
        self.df.drop(self.df.index[0:], inplace=True)
        self.df[temp_df.columns]=temp_df
        self.refresh()
    
    def insert_row(self):
        focus = self.tree.focus()
        if focus == '':
            return
        idx = int(focus)
        new_row = self.row_editor()
        _df_insert_row_inplace(self.df, idx, new_row)
        self.refresh()
    
    def move_row(self):
        pa, pb = 'Row To Move:', 'Move Before:'
        row_list = list(self.df.index)
        oa = _numberlist(row_list)
        ob = _numberlist(row_list + ['move to end'])
        values = _multi_input(self, (pa, pb), options={pa:oa, pb:ob})
        if values:
            va, vb = values
            ai = oa.index(va)
            bi = ob.index(vb)
            if ai <= bi:
                bi -= 1
            row = self.df.iloc[ai:ai+1, :]
            _df_drop_row_inplace(self.df, ai)
            _df_insert_row_inplace(self.df, bi, row)
        self.refresh()
    
    def edit_row(self):
        focus = self.tree.focus()
        if focus == '':
            return
        idx = int(focus)
        new_row = self.row_editor(idx)
        _df_drop_row_inplace(self.df, idx)
        _df_insert_row_inplace(self.df, idx, new_row)
        self.refresh()
    
    def delete_row(self):
        focus = self.tree.focus()
        if focus == '':
            return
        idx = int(focus)
        _df_drop_row_inplace(self.df, idx)
        self.refresh()
    
    def add_column(self):
        values = _multi_input(self, ('Column Name',))
        if values:
            name = values[0]
            self.df[name]=''
        self.refresh()

    def move_column(self):
        pa, pb = 'Column To Move:', 'Move Before:'
        column_list = list(self.df.columns.values)
        oa = _numberlist(column_list)
        ob = _numberlist(column_list + ['move to end'])
        values = _multi_input(self, (pa, pb), options={pa:oa, pb:ob})
        if values:
            va, vb = values
            ai = oa.index(va)
            bi = ob.index(vb)
            if ai <= bi:
                bi -= 1
            name = column_list[ai]
            column = self.df.iloc[:, ai]
            _df_delete_column_inplace(self.df, ai)
            self.df.insert(bi, name, column)
        self.refresh()
    
    def delete_column(self):
        column_list = list(self.df.columns.values)
        column_list_i = _numberlist(column_list)
        prompt = 'Column To Delete:'
        values = _multi_input(self, (prompt,),options={prompt:column_list_i})
        if values:
            ai = column_list_i.index(values[0])
            _df_delete_column_inplace(self.df, ai)
        self.refresh()
    
    def row_editor(self, idx=None):
        columns = _get_df_head(self.df)
        defaults=None
        if idx is not None:
            defaults = _get_df_row(self.df, idx)
        values = _multi_input(self, columns, 'Row Editor', defaults)
        if values:
            new_row = pd.DataFrame([values], columns=columns)
            new_row.set_index(self.df.index.names, inplace=True)
            return new_row
        return None
    
    def set_index(self):
        columns = _get_df_head(self.df)
        fields = ['keep old index'] + columns
        tf = ('True','False')
        options = {column: tf for column in fields}
        values = _multi_input(self, fields, title='Select Index Columns',options=options)
        if values:
            keep_index = values.pop(0)
            index_columns = [c for v, c in zip(values, columns) if v == 'True']
            if keep_index=='True':
                self.df.reset_index(inplace=True)
            self.df.set_index(index_columns, inplace=True)
            self.refresh()



def _multi_input(root, fields, title='Input', defaults=None, options=None):
    input_root = tk.Toplevel(root)
    input_root.title(title)
    entries = []
    values = []
    if defaults == None:
        defaults = ('',)*len(fields)
    if options == None:
        options = {}
    for i, (field, default) in enumerate(zip(fields, defaults)):
        tk.Label(input_root, text=field).grid(row=i, column=0)
        if field in options:
            sv = tk.StringVar(input_root)
            tk.OptionMenu(input_root, sv, *options[field]).grid(row=i, column=1)
            entries.append(sv)
        else:
            entry = tk.Entry(input_root)
            entry.grid(row=i, column=1)
            entry.insert(0, str(default))
            entries.append(entry)
    def save():
        values.extend([entry.get() for entry in entries])
        input_root.destroy()
    tk.Button(input_root, text='Save', command=save).grid(row=i+1, column=0)
    root.wait_window(input_root)
    return values


def _numberlist(x):
    return [str(i) + '. ' + str(xi) for i, xi in enumerate(x)]


def _get_df_row(df, idx):
    index = df.index[idx]
    if isinstance(index, tuple):
        index = list(index)
    else:
        index = [index]
    values = list(df.iloc[idx, :])
    row = index + values
    return row


def _get_df_head(df):
    columns = list(df.columns)
    index_col = list(df.index.names)
    head = index_col + columns
    return head


def _df_drop_row_inplace(df, idx):
    a = df.iloc[:idx, :]
    b = df.iloc[idx+1:, :]
    temp = pd.concat([a,b],copy=False,ignore_index=False)
    df.drop(df.index[0:], inplace=True)
    df[temp.columns] = temp


def _df_insert_row_inplace(df, idx, row):
    a = df.iloc[:idx, :]
    b = df.iloc[idx:, :]
    temp = pd.concat([a,row,b],copy=False,ignore_index=False)
    df.drop(df.index[0:], inplace=True)
    df[temp.columns] = temp


def _df_delete_column_inplace(df, idx):
    column_list = list(df.columns.values)
    column_list[idx] = '__TO DELETE__'
    df.columns = column_list
    df.drop('__TO DELETE__', axis=1, inplace=True)


def _edit_csv():
    """open a csv in DFEditor and optionally save on close"""
    fp = filedialog.askopenfile(title='Select CSV file to open.')
    df = pd.read_csv(fp)
    root = tk.Tk()
    TKTable(root, df, buttons=ALL).pack(side='top', expand=True, fill='both')
    root.mainloop()
    root = tk.Tk()
    tk.Label(root, text='Save the DataFrame?').grid(row=0,column=0)
    def save():
        df.to_csv(fp.name, index=False)
        root.destroy()
    tk.Button(root, text='Save', command=save).grid(row=1,column=0)
    def cancel():
        root.destroy()
    tk.Button(root, text='Cancel', command=cancel).grid(row=1,column=1)
    root.mainloop()


if __name__ == '__main__':
    _edit_csv()