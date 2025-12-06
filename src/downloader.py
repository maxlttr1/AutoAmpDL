from tracks import Track

import subprocess
from pathlib import Path

def fetch_playlist(url: str, indexes: str | None, archive_file: Path) -> list[Track]:
    idsArchive = []
    if archive_file:
        with open(archive_file, 'r') as f:
            for line in f:
                idsArchive.append(line.strip().removeprefix("youtube "))

    print("\033[34m🔍 Fetching playlist information...\033[0m")

    cmd = [
        "yt-dlp",
        url, 
        "--print", "%(id)s|%(title)s",
        "--flat-playlist"
    ]

    if indexes:
        cmd.extend(["--playlist-items", indexes])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0 or not result.stdout:
        raise RuntimeError("❌ Failed to get video info from playlist.")

    lines = result.stdout.strip().splitlines()
    tracks = []
    for line in lines:
        video_id, title = line.split("|", 1)
        if not(video_id.strip() in idsArchive):
            tracks.append(Track(video_id=video_id.strip(), title=title.strip()))

    print(f"\033[32m🎵 Found {len(tracks)} tracks to download:\033[0m")

    return tracks

def download_playlist(url : str, cookies_path: Path, target_dir: Path, indexes: str | None) -> list[Path]:
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
            "--download-archive", "ids.txt",
            url
        ]

        if indexes:
            cmd.extend(["--playlist-items", indexes])
        
        result = subprocess.run(cmd)

    except subprocess.TimeoutExpired:
        raise RuntimeError("❌ Download timed out\n")
    except Exception:
        raise RuntimeError("❌ Unexpected error during download\n")

    print(f"\n\033[32m✅ Download completed for {url}\033[0m\n")

    return [file for file in target_dir.iterdir() if file.is_file()]

