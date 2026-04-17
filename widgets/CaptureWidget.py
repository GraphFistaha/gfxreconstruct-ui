import pathlib
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from functools import partial

def BrowseDirectory(parent, output: tk.StringVar, title: str):
    # Open file dialog to select a directory
    filename = filedialog.askdirectory(parent=parent, title=title)
    if filename:
        output.set(filename)
        return True
    return False


def BrowseExecutable(parent, output: tk.StringVar, title: str):
    filetypes = []
    if sys.platform == "win32":  # Windows
        filetypes = [
            ("Executable files", "*.exe"),
            ("Batch files", "*.bat"),
            ("Command files", "*.cmd"),
            ("PowerShell scripts", "*.ps1"),
            ("All files", "*.*"),
        ]
    elif sys.platform == "darwin":  # macOS
        filetypes = [
            ("Applications", "*.app"),
            ("Unix executables", "*"),
            ("Shell scripts", "*.sh"),
            ("All files", "*"),
        ]
    else:  # Linux and other Unix-like
        filetypes = [
            ("Executable files", "*"),
            ("Shell scripts", "*.sh"),
            ("Python scripts", "*.py"),
            ("Perl scripts", "*.pl"),
            ("Ruby scripts", "*.rb"),
            ("Binary files", "*.bin"),
            ("All files", "*"),
        ]
    # Open file dialog to select a file
    filename = filedialog.askopenfilename(
        parent=parent, title=title, filetypes=filetypes
    )
    if filename:
        output.set(filename)
        return True
    return False


def CaptureTraceWidget(app: tk.Tk) -> tuple[pathlib.Path, str, pathlib.Path]:
    result = (pathlib.Path(), "", pathlib.Path())
    widget = tk.Toplevel(app)
    widget.title("Capture trace")
    widget.transient(app)
    widget.grab_set()
    widget.geometry()

    widget_frame = ttk.Frame(widget, style="Modal.TFrame", padding="20")
    widget_frame.pack(fill="both", expand=True)

    # File selection section
    executable_frame = ttk.Frame(widget_frame)
    executable_frame.pack(fill="x", pady=(0, 15))

    # Select executable file
    path_frame = ttk.Frame(executable_frame)
    path_frame.pack(fill="x")
    # TODO: place label on left side
    tk.Label(path_frame, text="Executable", justify=tk.LEFT, anchor="w").pack()
    executable_path = tk.StringVar()
    ttk.Entry(path_frame, textvariable=executable_path).pack(
        side="left", fill="x", expand=True, padx=(0, 10)
    )
    ttk.Button(
        path_frame,
        text="Browse...",
        command=partial(
            BrowseExecutable,
            widget,
            output=executable_path,
            title="Select executable to capture",
        ),
    ).pack(side="right")

    # input executable arguments
    args_frame = ttk.Frame(executable_frame)
    args_frame.pack(fill="x")
    # TODO: place label on left side
    tk.Label(args_frame, text="Arguments", justify=tk.LEFT, anchor="w").pack()
    args_string = tk.StringVar()
    ttk.Entry(args_frame, textvariable=args_string).pack(fill="x")

    # Select working directory
    working_directory_frame = ttk.Frame(executable_frame)
    working_directory_frame.pack(fill="x")
    # TODO: place label on left side
    tk.Label(
        working_directory_frame, text="Working directory", justify=tk.LEFT, anchor="w"
    ).pack()
    working_directory_path = tk.StringVar()
    ttk.Entry(working_directory_frame, textvariable=working_directory_path).pack(
        side="left", fill="x", expand=True, padx=(0, 10)
    )
    ttk.Button(
        working_directory_frame,
        text="Browse...",
        command=partial(
            BrowseDirectory,
            widget,
            output=working_directory_frame,
            title="Select working directory",
        ),
    ).pack(side="right")

    def ok():
        nonlocal result
        exe = pathlib.Path(executable_path.get())
        if exe.is_file():
            wd = pathlib.Path(working_directory_path.get())
            if wd.is_dir():
                wd = exe.parent
            result = (
                exe,
                args_string.get(),
                wd,
            )
            widget.destroy()
        else:
            print("Select executable to run gfxreconstruct")

    button_frame = ttk.Frame(widget_frame)
    button_frame.pack(fill="x")
    ttk.Button(
        button_frame,
        text="Run",
        command=ok,
        width=10,
    ).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=widget.destroy, width=10).pack(
        side="right"
    )
    app.wait_window(widget)
    return result