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
    def __init__(self, parent:tk.Widget, df:pd.DataFrame, 
                 buttons:tuple[str,...]=VIEW_ONLY, 
                 custom_buttons:tuple[tuple[str, typing.Callable],...]=NONE):
        """A Tkinter Widget to display and edit a DataFrame

        DataFrame edits are done without reassigning the DataFrame
        variable, meaning that existing references to the DataFrame
        will continue to work.

        parent: the parent tk Widget that TkTable will pack/grid into

        df: the dataframe to display / edit

        buttons: tuple of button names (APPEND_ROW, INSERT_ROW, MOVE_ROW, 
        EDIT_ROW, DELETE_ROW, APPEND_COLUMN, MOVE_COLUMN, DELETE_COLUMN,
        SET_INDEX, REFRESH) or preset group (NONE, ALL, VIEW_ONLY, ROW_ONLY, 
        COLUMN_ONLY)

        custom buttons: tuple of (label, function) pairs to create buttons"""

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
        hd = _apply_temp_index(self.df)
        self.tree['columns'] = ['[' + str(hd[i]) + ']' 
                                if i < 0 else 
                                hd[i] 
                                for i in self.df.columns]
        for column in self.tree['columns']:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)
        for i in self.df.index:
            self.tree.insert('', 'end', i, values=list(self.df.loc[i]))
        _unapply_temp_index(self.df, hd)
        print(self.df)
    
    def append_row(self, values:list=None):
        self.row_editor(new=True, values=values)
    
    def insert_row(self, idx:int=None, values:list=None):
        if idx is None:
            focus = self.tree.focus()
            if focus == '':
                return
            idx = int(focus)
        self.row_editor(idx=idx, values=values, new=True)

    def edit_row(self):
        focus = self.tree.focus()
        if focus == '':
            return
        idx = int(focus)
        self.row_editor(idx=idx, new=False)
    
    def row_editor(self, idx:int=None, new:bool=True, values:list=None):
        if new is False and idx is None:
            return  # this combination is not allowed
        columns = _get_df_head(self.df)
        hd = _apply_temp_index(self.df)
        if values is None:
            defaults = None if new is True else list(self.df.loc[idx])
            values = _multi_input(self, columns, 'Row Editor', defaults)
        if values is not None:
            if idx is None:
                idx2 = self.df.shape[0] + 1
            else:
                idx2 = idx - 0.5 * new
            self.df.loc[idx2] = values
            self.df.sort_index(ascending=True, inplace=True)
        _unapply_temp_index(self.df, hd)
        self.refresh()
    
    def move_row(self):
        pa, pb = 'Row To Move:', 'Move Before:'
        row_list = list(self.df.index)
        oa = _numberlist(row_list)
        ob = _numberlist(row_list + ['move to end'])
        values = _multi_input(self, (pa, pb), options={pa:oa, pb:ob})
        if values is None:
            return
        va, vb = values
        ai, bi = oa.index(va), ob.index(vb)
        hd = _apply_temp_index(self.df)
        new_index = self.df.index.to_list()
        new_index[ai] = bi - 0.5
        self.df['__new_index__']=new_index
        self.df.set_index('__new_index__', inplace=True)
        self.df.sort_index(ascending=True, inplace=True)
        _unapply_temp_index(self.df, hd)
        self.refresh()

    def delete_row(self):
        focus = self.tree.focus()
        if focus == '':
            return
        idx = int(focus)
        hd = _apply_temp_index(self.df)
        self.df.drop(idx, inplace=True)
        _unapply_temp_index(self.df, hd)
        self.refresh()
    
    def add_column(self):
        fields = ['Column Name'] + list(self.df.index)
        values = _multi_input(self, fields)
        if values:
            name = values[0]
            self.df[name]=values[1:]
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
            hd = _apply_temp_index(self.df)
            self.df.rename(columns={bi: bi + .5, ai:bi}, inplace=True)
            hd[bi + .5] = hd[bi] if bi in hd else None
            hd[bi]=hd[ai]
            self.df.sort_index(axis=1, inplace=True)
            _unapply_temp_index(self.df, hd)
        self.refresh()
    
    def delete_column(self):
        column_list = list(self.df.columns.values)
        column_list_i = _numberlist(column_list)
        prompt = 'Column To Delete:'
        values = _multi_input(self, (prompt,),options={prompt:column_list_i})
        if values:
            ai = column_list_i.index(values[0])
            hd = _apply_temp_index(self.df)
            self.df.drop(ai, inplace=True, axis=1)
            _unapply_temp_index(self.df, hd)
        self.refresh()

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
            if index_columns:
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


def _get_df_head(df):
    columns = list(df.columns)
    index_col = list(df.index.names)
    head = index_col + columns
    return head


def _apply_temp_index(df):
    # replace column names and index names with known sequential values
    # ensures no duplicates in index and column names
    # reset index - ensures no duplicates in index
    # returns a dictionary of {temporary: real} index and column names
    temp_index = list(range(-len(df.index.names), 0))
    temp_columns = list(range(len(df.columns)))
    header_dict ={k:v for k,v in 
                  zip(temp_index + temp_columns, 
                      list(df.index.names) + list(df.columns))}
    df.index.names = temp_index
    df.columns = temp_columns
    df.reset_index(drop=False, inplace=True)
    return header_dict


def _unapply_temp_index(df, header_dict):
    # return a DataFrame to its original index and column names based
    # on supplied header_dict of {temporary: real} index and column names
    # Index columns should be < 0 and other columns should be > 0
    index_columns = [c for c in df.columns if c < 0]
    df.set_index(index_columns, inplace=True)
    index_names = [header_dict[i] for i in df.index.names]
    df.index.names = index_names
    column_names = [header_dict[c] for c in df.columns]
    df.columns = column_names


def _edit_csv():
    """open a csv in DFEditor and optionally save on close"""
    fp = filedialog.askopenfile(title='Select CSV file to open.')
    df = pd.read_csv(fp)
    root = tk.Tk()
    TkTable(root, df, buttons=ALL).pack(side='top', expand=True, fill='both')
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
