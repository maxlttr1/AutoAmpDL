import os
import concurrent.futures
import subprocess
import shutil
import sys
import argparse
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

def dependencies_check():
    # Check for dependencies
    if shutil.which("ffmpeg") is None:
        print("❌ ffmpeg is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)
    if shutil.which("yt-dlp") is None:
        print("❌ yt-dlp is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)

def playlist_fetch(url):
    print("🔍 Fetching playlist information...")
    # Get titles and IDs
    result = subprocess.run(["yt-dlp", url, "--print", "%(id)s|%(title)s", "--flat-playlist"], capture_output=True, text=True)

    if result.returncode != 0 or not result.stdout:
        print("❌ Failed to get video info from playlist.")
        sys.exit(1)

    ids = result.stdout.strip().splitlines()
    ids = [id.split('|', 1) for id in ids] # Split only the first |
    for id in ids:
        if len(id) > 2:
            print(id)
    print(f"🎵 Found {len(ids)} tracks to download:\n")

    return ids

def sanitize_filename(name):
    return ''.join(c for c in name if c not in r'\/:*?"<>|').replace('\xa0', ' ').strip()

def download_file(url, file):
    # Download as flac
    print(f"⬇️ Starting download for {file}...")

    result = subprocess.run(["yt-dlp", "--cookies-from-browser", "firefox", "-f", "bestaudio", "--extract-audio", "--audio-quality", "0", "--audio-format", "flac", "--quiet", "-o", "./%(title)s [%(id)s].%(ext)s", url], capture_output=True, text=True)

    output = result.stdout + result.stderr

    if result.returncode != 0:
        print("❌ Download failed. Please check your internet connection and the URL.")
        sys.exit(1)

    # Look for common failure keywords
    if any(kw in output for kw in ["ERROR", "Failed", "Sign in to confirm", "Requested format is not available"]):
        print(f"❌ Download issue detected for {url}")
        err_log.write(f"URL: {url}\n")
        err_log.write(output + "\n\n")
        sys.exit(1)

    print(f"\n✅ Download completed for {file} !\n")

def normalize_file(file):
    # Check if file exists before processing
    if not os.path.isfile(file):
        print(f"⚠️ File '{file}' not found, skipping normalization.")
        return

    # Strip the original extension
    file_wo_ext = os.path.splitext(file)[0]
    normalized_file = f"normalized_{file_wo_ext}.flac"

    print(f"🔊 Normalizing loudness: {file}\n")
    result = subprocess.run(["ffmpeg", "-y", "-i", file, "-filter:a", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "a", "-map_metadata", "-1", normalized_file], capture_output=True)
    
    if result.returncode == 0:
        print(f"✅ Loudness normalization successful for '{file}'.\n")
        try:
            os.remove(file)
            os.rename(normalized_file, f"{file_wo_ext}.flac")
        except Exception as e:
            print(f"⚠️ Failed to replace original file: {e}")
    else:
        print(f"❌ Loudness normalization failed for '{file}'.\n")

def handle_file(file, normalize_only, id = None):
    if not(normalize_only):
        download_file(f"https://www.youtube.com/watch?v={id}", file)
    #normalize_file(file)

def handle_playlist(directory, normalize_only, ids = None):
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
    ) as progress:
        # Normalize each downloaded FLAC file
        if not normalize_only:
            os.chdir("./tmp")
            task = progress.add_task("Downloading & Normalizing tracks...", total=len(ids))

            with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(handle_file, f"{title} [{video_id}].flac", normalize_only, video_id): (video_id, title) for video_id, title in ids}
                for future in concurrent.futures.as_completed(futures):
                    progress.update(task, advance=1)

            # Move all files from ./tmp to ../                
            subprocess.run("mv ./* ../", shell=True)

            try:
                os.rmdir("../tmp")
                print("Directory ./tmp has been removed successfully")
            except OSError as error:
                print(error)
                print("Directory ./tmp can not be removed")
        else:
            files = os.listdir("./")
            task = progress.add_task("Downloading & Normalizing tracks...", total=len(files))

            with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(handle_file, file, normalize_only) for file in files}
                for future in concurrent.futures.as_completed(futures):
                    progress.update(task, advance=1)

def main(directory, url = None, normalize_only = False):
    dependencies_check()

    # Changes to the desired directory
    os.chdir(directory)

    if not(normalize_only):
        ids = playlist_fetch(url)

        # Create a temp directory
        dir = "tmp"
        try:
            os.mkdir(dir)
            print(f"Directory '{dir}' created successfully.")
        except FileExistsError:
            print(f"Directory '{dir}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{dir}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

        handle_playlist(directory, normalize_only, ids)
    else:
        handle_playlist(directory, normalize_only)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoAmpDL")

    # Exclusion for --url and --normalize-only
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL to download from (playlist or a single audio/video)')
    group.add_argument('--normalize-only', action='store_true', help='Run normalize-only mode')

    parser.add_argument('directory', nargs='?', default='.', help='Directory to save the download (default: current directory)')

    args = parser.parse_args()

    if not(os.path.isdir(args.directory)):
        print(f"{args.directory} not found. Please provide a correct directory")
        sys.exit(1)

    if args.normalize_only:
        main(args.directory, normalize_only = True)
    else:
        main(args.directory, args.url)