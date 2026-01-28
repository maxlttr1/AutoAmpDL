from State import State
from CleanState import CleanState
from Track import Track

from pathlib import Path

class CheckState(State):
	def __init__(self, context):
		self.context = context

	def execute(self):
		check_missing_tracks(self.context.tracks, self.context.downloaded_files)

		self.context.changeState(CleanState(self.context))
		self.context.execute()
			

def check_missing_tracks(tracks: list[Track], downloaded_files: list[Path]) -> list[Track]:
    downloaded_ids = []

    for file in downloaded_files:
        stem = file.stem
        if "[" in stem and "]" in stem:
            downloaded_ids.append(stem.split("[")[-1].split("]")[0].strip())
   
    missing_tracks = []

    for track in tracks:
        if f"{track.video_id}" not in downloaded_ids:
            missing_tracks.append(track)
            print(f"\033[31m❌ Missing: {track.title} ({track.video_id})\033[0m")

    if not missing_tracks:
        print("\033[32m✅ All tracks appear to be downloaded!\033[0m")


    return missing_tracks