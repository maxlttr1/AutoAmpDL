import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import threading
import subprocess

from dependencies import check_dependencies
from logic import launch_processes, arg_parser

target_dir = Path.cwd()
cookie_file = None
progress = None
root = None

def choose_directory(dir_label):
    global target_dir
    target_dir = Path(filedialog.askdirectory())
    dir_label.config(text=f"📁 {target_dir}")

def choose_cookie(cookie_label):
    global cookie_file
    cookie_file = Path(filedialog.askopenfilename())
    cookie_label.config(text=f"🍪 {cookie_file}")

def click_start(url_input: tk.Entry, target_dir: Path, cookie_file: Path, mode: tk.StringVar, start: tk.Spinbox, end: tk.Spinbox, logs: ScrolledText):      
    url = url_input.get().strip()

    start = start.get().strip()
    end = end.get().strip()
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
        print(f"Invalid index range: start={start}, end={end}")
        return

    mode = mode.get()
    download_only = (mode == "download_only")
    normalize_only = (mode == "normalize_only")

    threading.Thread(
        target=launch_processes,
        args=(normalize_only, download_only, target_dir, url, cookie_file, indexes, logs),
        daemon=True
    ).start()

def updateBar(index: int, total: int) -> None:
    global progress
    global root

    progress['value'] = index / total * 100
    root.update_idletasks()

def display_log(logs: ScrolledText, message: str) -> None:
    logs.config(state=tk.NORMAL)
    #logs.delete(1.0, tk.END)
    
    logs.insert(tk.END, f"{message}.\n")
    logs.see(tk.END)
    logs.update_idletasks()

    logs.config(state=tk.DISABLED)

def main() -> None:
    check_dependencies()
    try:
        #gui()
        arg_parser()
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C). Exiting gracefully.")

def gui():
    global target_dir
    global cookie_file
    global progress
    global root

    root = tk.Tk()
    root.title("AutoAmpDL")
    root.geometry("600x800")
    root.resizable(False, False)
    
    # === URL input section ===
    url_frame = tk.Frame(root)
    url_frame.pack(padx=10, pady=5)
    tk.Label(url_frame, text="Enter YouTube URL:").pack(anchor="w")
    url_input = tk.Entry(url_frame, width=70)
    url_input.pack()

    # === Folder selection section ===
    folder_frame = tk.Frame(root)
    folder_frame.pack(pady=5, anchor="w")
    dir_label = tk.Label(folder_frame, text=f"📁 {target_dir}", anchor="w")
    tk.Button(folder_frame, text="Choose Target Folder", command=lambda: choose_directory(dir_label)).pack(side="left", padx=10)
    dir_label.pack(side="left")

    # === Cookie file section ===
    cookie_frame = tk.Frame(root)
    cookie_frame.pack(pady=5, anchor="w")
    cookie_label = tk.Label(cookie_frame, text=f"🍪 {cookie_file}", anchor="w")
    tk.Button(cookie_frame, text="Choose Cookie File (Optionnal)", command=lambda: choose_cookie(cookie_label)).pack(side="left", padx=10)
    cookie_label.pack(side="left")
    
    # === Mode selection ===
    mode_frame = tk.LabelFrame(root, text="Mode", padx=0, pady=0)
    mode_frame.pack(padx=10, pady=5, fill="x")
    mode = tk.StringVar(value="download_normalize")
    tk.Radiobutton(mode_frame, text="Download and Normalize", variable=mode, value="download_normalize").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="Download only", variable=mode, value="download_only").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="Normalize only", variable=mode, value="normalize_only").pack(anchor="w")

    # === Range selection (Start/End) ===
    range_frame = tk.LabelFrame(root, text="Playlist Range", padx=10, pady=5)
    range_frame.pack(pady=5)
    tk.Label(range_frame, text="Start:").grid(row=0, column=0, padx=0, pady=0)
    start = tk.Spinbox(range_frame, from_=1, to=1000, width=6)
    start.grid(row=0, column=1, padx=0)
    tk.Label(range_frame, text="End:").grid(row=0, column=2, padx=0, pady=0)
    end = tk.Spinbox(range_frame, from_=1, to=1000, width=6)
    end.grid(row=0, column=3, padx=0)

    # === Start button ===
    tk.Button(
        root,
        text="▶ Start",
        bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
        command=lambda: click_start(url_input, target_dir, cookie_file, mode, start, end, logs),
        padx=30
    ).pack(pady=5)

    # === Log output ===
    log_frame = tk.LabelFrame(root, text="Logs", padx=0, pady=0)
    log_frame.pack(padx=10, pady=(0,10), fill="both", expand=True)
    logs = ScrolledText(log_frame, width=85, height=20, wrap=tk.WORD, state=tk.DISABLED)
    logs.pack(fill="both", expand=True)

    '''
    progress = ttk.Progressbar(root, length = 100, mode = 'determinate')
    progress.pack(pady=10, fill="x", padx=10)
    '''

    def on_closing():
        print("GUI is closing. Terminating subprocesses...")
        terminate_subprocesses()
        root.destroy()

    def terminate_subprocesses():
        from downloader import subprocesses as s1
        from normalizer import subprocesses as s2
        subprocesses = s1 + s2

        for proc in subprocesses:
            if proc.poll() is None:  # Check if process is still running
                proc.terminate()  # Gracefully terminate the subprocess
                proc.wait()  # Wait for the process to terminate
        subprocesses.clear()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle window close
    root.mainloop()

if __name__ == "__main__":
    main()