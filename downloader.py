from tracks import Track

import subprocess
from pathlib import Path

def fetch_playlist(url: str) -> list[Track]:
    print("🔍 Fetching playlist information...")
    result = subprocess.run(
        ["yt-dlp", url, "--print", "%(id)s|%(title)s", "--flat-playlist"],
        capture_output=True, text=True
    )

    if result.returncode != 0 or not result.stdout:
        raise RuntimeError("❌ Failed to get video info from playlist.")

    lines = result.stdout.strip().splitlines()
    tracks = []
    for line in lines:
        video_id, title = line.split("|", 1)
        tracks.append(Track(video_id=video_id.strip(), title=title.strip()))

    print(f"🎵 Found {len(tracks)} tracks to download:\n")
    return tracks


def download_track(track: Track, cookies_path: Path, target_dir: Path) -> Path:
    print(f"⬇️ Starting download for {track.title}...")

    output_template = str(target_dir / f"{track.title} [{track.video_id}].%(ext)s")

    try:
        result = subprocess.run([
            "yt-dlp",
            #"--cookies", str(cookies_path),
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-quality", "0",
            "--audio-format", "flac",
            "--quiet",
            #"--extractor-args", "youtube:player_client=mweb", # Avoid YouTube's SABR streaming (which breaks normal format URLs)
            "-o", output_template,
            f"https://www.youtube.com/watch?v={track.video_id}"
        ], capture_output=True, text=True, timeout=300)  # e.g., 5 min timeout

        output = result.stdout + result.stderr

        if result.returncode != 0 or any(kw in output for kw in ["ERROR", "Failed", "Sign in to confirm", "Requested format is not available"]):
            raise RuntimeError(f"❌ Download issue detected for {track.video_id}\n{output}")

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"❌ Download timed out for {track.video_id}\n")
    except Exception as e:
        # Catch all other exceptions
        raise RuntimeError(f"❌ Unexpected error during download of {track.video_id}: {e}\n")

    print(f"\n✅ Download completed for {track.title}!\n")
    return target_dir / f"{track.title} [{track.video_id}].flac"
