from State import State
from DownloadState import DownloadState
from Track import Track

from pathlib import Path
import subprocess

class FetchState(State):
	def __init__(self, context):
		self.context = context

	def execute(self):
		self.context.addTrack(fetch_playlist(
			self.context.url,
			self.context.indexes,
			self.context.archive_file
		))

		self.context.changeState(DownloadState(self.context))
		self.context.execute()



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
