import os
import concurrent.futures
import subprocess
import shutil
import sys

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
    ids = [id.split('|') for id in ids]
    print(f"🎵 Found {len(ids)} tracks to download:\n")

    return ids

def download_file(url, file):
    # Download as flac
    print(f"⬇️ Starting download for {file}...")

    result = subprocess.run(["yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-quality", "0", "--audio-format", "flac", "--quiet", "-o", "./%(title)s [%(id)s].%(ext)s", url])

    if result.returncode != 0:
        print("❌ Download failed. Please check your internet connection and the URL.")
        sys.exit(1)

    print("\n✅ Download completed!\n")

def normalize_file(file):
    # Check if file exists before processing
    if not os.path.isfile(file):
        print(f"⚠️ File '{file}' not found, skipping normalization.")
        return

    normalized_file = "normalized_" + file

    print(f"🎚️ Normalizing loudness: {file}")
    result = subprocess.run(["ffmpeg", "-y", "-i", file, "-filter:a", "loudnorm=I=-14:TP=-1.5:LRA=11", normalized_file], capture_output=True)
    
    if result.returncode == 0:
        print(f"✅ Loudness normalization successful for '{file}'.\n")
        try:
            os.remove(file)
            os.rename(normalized_file, file)
            shutil.move(file, "../")
        except Exception as e:
            print(f"⚠️ Failed to replace original file: {e}")
    else:
        print(f"❌ Loudness normalization failed for '{file}'.")

def handle_file(id, file):
    download_file(f"https://www.youtube.com/watch?v={id}", file)
    normalize_file(file)

def handle_playlist(ids):
    # Normalize each downloaded FLAC file
    files = os.listdir("./tmp/")
    os.chdir("./tmp")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(handle_file, video_id, f"{title} [{video_id}].flac"): (video_id, title) for video_id, title in ids}
    
    try:
        os.rmdir("../tmp")
        print("Directory ./tmp has been removed successfully")
    except OSError as error:
        print(error)
        print("Directory ./tmp can not be removed")

def main(url):
    dependencies_check()
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

    handle_playlist(ids)

    print("🎉 All done! Your tracks are downloaded and normalized.")

if __name__ == "__main__":
    '''if len(sys.argv) > 1:
        url = sys.argv[1]
        print(sys.argv)
    else:
        print("Please add an url to start the download.")
        sys.exit(1)'''
    main("https://www.youtube.com/playlist?list=PLkF8ZEu4FB1nm_omaMwtZ5wIO7S-01uCu")