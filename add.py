import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

from pathlib import Path
import threading
import subprocess

# -----------------------------
# Function to run yt-dlp
# -----------------------------
def download_audio(url: str, target_dir: Path, log_display: ScrolledText):
    if not url.strip():
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    log_path = target_dir / "yt-dlp-log.txt"
    output_template = str(target_dir / "%(title)s [%(id)s].%(ext)s")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-quality", "0",
        "--audio-format", "flac",
        "--restrict-filenames",
        "-o", output_template,
        "--cookies", "./cookies.txt",
        url
    ]

    try:
        with open(log_path, "w", encoding="utf-8") as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            log_display.config(state=tk.NORMAL)
            log_display.delete(1.0, tk.END)

            for line in process.stdout:
                log_file.write(line)
                log_display.insert(tk.END, line)
                log_display.see(tk.END)  # Scroll to latest line
                log_display.update_idletasks()

            process.wait()
            log_display.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")



# -----------------------------
# Function to read and show log
# -----------------------------
def display_log(log_path: Path, text_widget: ScrolledText):
    if not log_path.exists():
        text_widget.insert(tk.END, "Log file not found.\n")
        return

    with open(log_path, "r", encoding="utf-8") as file:
        log_contents = file.read()

    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, log_contents)
    text_widget.config(state=tk.DISABLED)


# -----------------------------
# Button click handler
# -----------------------------
def on_download_click(entry: tk.Entry, log_display: ScrolledText):
    url = entry.get()
    target_dir = Path.cwd()

    # Run in a thread so GUI stays responsive
    threading.Thread(
        target=download_audio,
        args=(url, target_dir, log_display),
        daemon=True
    ).start()

def choose_directory():
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        print("Selected directory:", selected_dir)
        # You can also store it in a global or pass to download logic

# -----------------------------
# GUI Setup
# -----------------------------
def create_gui():
    root = tk.Tk()
    root.title("Music Downloader with Log Viewer")
    root.geometry("700x500")

    # URL Input
    tk.Label(root, text="Enter YouTube URL:").pack(pady=(10, 0))
    url_entry = tk.Entry(root, width=80)
    url_entry.pack(pady=5)

    tk.Button(root, text="Choose Download Folder", command=choose_directory).pack(pady=5)


    # Download Button
    tk.Button(
        root,
        text="Download",
        command=lambda: on_download_click(url_entry, log_display)
    ).pack(pady=10)

    # Log Display
    log_display = ScrolledText(root, width=85, height=25, wrap=tk.WORD)
    log_display.pack(padx=10, pady=10)
    log_display.config(state=tk.DISABLED)

    root.mainloop()


# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    create_gui()
