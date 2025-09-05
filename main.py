import os
import concurrent.futures
import subprocess
import shutil
import sys

def main(url):
    # Check for dependencies
    if shutil.which("ffmpeg") is None:
        print("❌ ffmpeg is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)
    if shutil.which("yt-dlp") is None:
        print("❌ yt-dlp is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)
    
    print("🔍 Fetching playlist information (this may take some time)...")
    # Get titles and IDs
    result = subprocess.run(["yt-dlp", url, "--print", '%(id)s', "--flat-playlist"], capture_output=True, text=True)

    if result.returncode != 0 or not result.stdout:
        print("❌ Failed to get video info from playlist.")
        sys.exit(1)

    print(f"🎵 Found {len(result.stdout.strip().splitlines())} tracks to download:\n")
    
    # Download as flac
    print("⬇️ Starting download and conversion to FLAC (this may take some time)...")

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
        
    result = subprocess.run(["yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-quality", "0", "--audio-format", "flac", "--progress", "" "-o", "./tmp/%(title)s [%(id)s].%(ext)s", url])

    if result.returncode != 0:
        print("❌ Download failed. Please check your internet connection and the playlist URL.")
        sys.exit(1)

    print("\n✅ Download completed! Starting loudness normalization for each track...\n")

    # Normalize each downloaded FLAC file
    files = os.listdir("./tmp/")
    os.chdir("./tmp")
    for file in files:
        # Check if file exists before processing
        if not os.path.isfile(file):
            print(f"⚠️ File '{file}' not found, skipping normalization.")
            continue

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
    
    print("🎉 All done! Your tracks are downloaded and normalized.")

if __name__ == "__main__":
    url = "https://www.youtube.com/playlist?list=PLTo6svdhIL1cxS4ffGueFpVCF756ip-ab"
    '''if len(sys.argv) > 1:
        url = sys.argv[1]
        print(sys.argv)
    else:
        print("Please add an url to start the download.")
        sys.exit(1)'''
    main(url)