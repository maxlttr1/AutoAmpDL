import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import threading

from dependencies import check_dependencies
from logic import arg_parser

def choose_directory():
    target_dir = filedialog.askdirectory()
    if target_dir:
        print(f"Selected directory: {target_dir}")

def click_start(url_input: tk.Entry, mode: tk.Entry, start: tk.Entry, end: tk.Entry):
    target_dir = Path.cwd()
    
    url = url_input.get()

    start = start.get()
    end = end.get()
    indexes = ""
    if start and end and int(start) < int(end):
        indexes = f"{start}-{end}"
    elif start and end and int(start) == int(end):
        indexes = f"{start}"
    elif start and not(end) and int(start) >= 1:
        indexes = f"{start}-"
    elif not(start) and end and int(end) > 1:
        indexes = f"1-{end}"
    elif not(start) and not(end):
        indexes = ""
    else:
        print(f"Index start: {start}, Index end: {end}. Please provide correct Index values")
        return

    mode = mode.get()
    download_only = False
    normalize_only = False
    if mode == "download_only":
        download_only = True
    elif mode == "normalize_only":
        normalize_only = True

    print(target_dir, url, mode, indexes)
    '''threading.Thread(
        target=download_audio,
        args=(url, target_dir, log_display),
        daemon=True
    ).start()'''

def main() -> None:
    check_dependencies()
    try:
        gui()
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C). Exiting gracefully.")

def gui():
    root = tk.Tk()
    root.title("AutoAmpDL")
    root.geometry("700x500")

    tk.Button(root, text="Choose Download Folder", command=choose_directory).pack(pady=0)

    tk.Label(root, text="Enter YouTube URL:").pack(pady=(0, 0))
    url_input = tk.Entry(root, width=80)
    url_input.pack(pady=(0,0))

    mode = tk.StringVar(value="download_normalize")  # default selection
    tk.Radiobutton(root, text="Download and Normalize", variable=mode, value="download_normalize").pack(pady=0)
    tk.Radiobutton(root, text="Download only", variable=mode, value="download_only").pack(pady=0)
    tk.Radiobutton(root, text="Normalize only", variable=mode, value="normalize_only").pack(pady=0)

    tk.Label(root, text="Start").pack(pady=(0, 0))
    start = tk.Spinbox(root, from_=0, to=1000, width=5)
    start.pack(pady=(0,0))
    tk.Label(root, text="End").pack(pady=(0, 0))
    end = tk.Spinbox(root, from_=0, to=1000, width=5)
    end.pack(pady=(0,0))

    tk.Button(
        root,
        text="Start",
        command=lambda: click_start(url_input, mode, start, end)
    ).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()