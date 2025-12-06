import shutil
import sys

def check_dependencies() -> None:
    if shutil.which("ffmpeg") is None:
        print("❌ ffmpeg is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)
    if shutil.which("yt-dlp") is None:
        print("❌ yt-dlp is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)