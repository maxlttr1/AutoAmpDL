from tracks import Track

import subprocess
from pathlib import Path

subprocesses = []

def fetch_playlist(url: str, indexes: str | None) -> list[Track]:
    global subprocesses
    
    print("\033[34m🔍 Fetching playlist information...\033[0m")

    cmd = [
        "yt-dlp",
        url, 
        "--print", "%(id)s|%(title)s",
        "--flat-playlist"
    ]

    if indexes:
        cmd.extend(["--playlist-items", indexes])

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocesses.append(proc)
    stdout, stderr = proc.communicate()  # Capture the output and error

    if proc.returncode != 0 or not stdout:
        raise RuntimeError("❌ Failed to get video info from playlist.")

    lines = stdout.strip().splitlines()
    tracks = []
    for line in lines:
        video_id, title = line.split("|", 1)
        tracks.append(Track(video_id=video_id.strip(), title=title.strip()))

    print(f"\033[32m🎵 Found {len(tracks)} tracks to download:\033[0m")

    return tracks

def download_playlist(url : str, cookies_path: Path, target_dir: Path, indexes: str | None) -> list[Path]:
    global subprocesses
    print(f"⬇️ Starting download of the playlist: {url} ...")

    output_template = str(target_dir / "%(title)s [%(id)s].%(ext)s")

    try:
        cmd = [
            "yt-dlp",
            #"-f", "bestaudio",
            "--cookies", str(cookies_path),
            "--extract-audio",
            "--audio-quality", "0",
            "--audio-format", "flac",
            "--restrict-filenames", # Restrict filenames to only ASCII characters, and avoid "&" and spaces in filenames
            "-o", output_template,
            url
        ]

        if indexes:
            cmd.extend(["--playlist-items", indexes])
        
        proc = subprocess.Popen(cmd)
        subprocesses.append(proc)

        stdout, stderr = proc.communicate()  # Capture the output and error

    except subprocess.TimeoutExpired:
        raise RuntimeError("❌ Download timed out\n")
    except Exception:
        raise RuntimeError("❌ Unexpected error during download\n")

    print(f"\n\033[32m✅ Download completed for {url}\033[0m\n")

    return [file for file in target_dir.iterdir() if file.is_file()]

