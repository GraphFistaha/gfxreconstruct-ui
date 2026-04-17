#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import pathlib
import sys, os
import json
import pandas as pd
from pandastable import Table, TableModel

from TraceView import buildTraceView, COLUMNS
from widgets.CaptureWidget import CaptureTraceWidget

APPLICATION_TITLE = "gfxreconstruct-ui"
APPLICATION_DEFSIZE = "800x600"
CACHE_DIRECTORY = pathlib.Path(os.getcwd() + "/.cache")
CAPTURE_SCRIPT = pathlib.Path(os.getenv("VULKAN_SDK")) / "Bin/gfxrecon-capture-vulkan.py"
CONVERT_SCRIPT = pathlib.Path(os.getenv("VULKAN_SDK")) / "Bin/gfxrecon-convert.exe"

g_currentTraceDf: pd.DataFrame = None
g_treeView : Table = None
g_selectionView : tk.Text = None


def BrowseTraceFile(parent, output: tk.StringVar, title: str):
    filetypes = []
    # Open file dialog to select a file
    filename = filedialog.askopenfilename(
        parent=parent, title=title, filetypes=[("GFXReconstruct trace files", "*.gfxr"), ("All files", "*.*")]
    )
    if filename:
        output.set(filename)
        return True
    return False


def OpenFile(app: tk.Tk, filename :pathlib.Path):
    global g_currentTraceDf
    global g_treeView
    if not filename.is_file() or not filename.exists():
        return False
    
    result = subprocess.run([CONVERT_SCRIPT, "--format", "json", filename.as_posix()])
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return False
    result_file = filename.with_suffix('.json')
    with open(result_file, mode='r', encoding='utf-8') as f:
        js = json.load(f)
        g_currentTraceDf = buildTraceView(js)
        df_subset = g_currentTraceDf[['function', 'frame']] 
        g_treeView.updateModel(TableModel(df_subset))
        g_treeView.redraw()
    os.remove(result_file)


def CreateMainUI(app: tk.Tk):
    def onCapture():
        exe, args, working_dir = CaptureTraceWidget(app)
        if exe.is_file():
            out_file = working_dir / (exe.stem + ".gfxr") 
            try:
                result = subprocess.run(["python", CAPTURE_SCRIPT, "--no-file-timestamp", "-o", out_file.as_posix(), exe.as_posix()], capture_output=True, cwd=exe.parent)
            except SystemExit:
                print("the script was crashed") 
            print('Output:\n', result.stdout.decode('utf-8'))
            if 0 != result.returncode:
                print('Errors:\n', result.stderr.decode('utf-8'))
            else:
                OpenFile(app, out_file)

    def onOpen():
        path = tk.StringVar()
        if BrowseTraceFile(app, path, "Select trace file to open"):
            OpenFile(app, pathlib.Path(path.get()))

    def onSelectFunc(event):
        g_treeView.handle_left_click(event)
        g_selectionView.delete("1.0", tk.END);
        # Get the row index that was clicked
        rowIndex = g_treeView.get_row_clicked(event)
        if rowIndex is not None:
            r = g_treeView.model.df.iloc[rowIndex]
            g_selectionView.insert("1.0", g_currentTraceDf.loc[r.name, 'full_info'])


    # Menubar
    menubar = tk.Menu(app)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Capture", command=onCapture)
    file_menu.add_command(label="Open trace", command=onOpen)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.quit)
    # Add File menu to the menubar
    menubar.add_cascade(label="File", menu=file_menu)
    app.config(menu=menubar)

    # Create a PanedWindow
    paned = ttk.Panedwindow(app, orient=tk.VERTICAL)
    paned.pack(fill=tk.BOTH, expand=True)

    # build treeview
    global g_treeView
    global g_currentTraceDf
    global g_selectionView
    table_frame = tk.Frame(paned)
    table_frame.pack(fill='both', expand=True)
    g_currentTraceDf =  pd.DataFrame([], columns=COLUMNS)
    g_treeView = Table(table_frame, TableModel(g_currentTraceDf), editable=False, enable_menus=False)
    g_treeView.show()


    info_frame = tk.Frame(paned)
    info_frame.pack(fill='both', expand=True)
    g_selectionView = tk.Text(info_frame)
    g_selectionView.pack(fill='both')

    paned.add(table_frame, weight=1)
    paned.add(info_frame, weight=3)

    g_treeView.bind('<Button-1>', onSelectFunc)
    g_treeView.rowheader.bind('<Button-1>', onSelectFunc)



if __name__ == "__main__":
    app = tk.Tk()
    app.title(APPLICATION_TITLE)
    app.geometry(APPLICATION_DEFSIZE)
    CreateMainUI(app)
    app.mainloop()
