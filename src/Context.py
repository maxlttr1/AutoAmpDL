from State import State
from InitState import InitState
from Track import Track

from pathlib import Path
from typing import Optional

class Context:
	state: State

	normalize_only: bool
	download_only: bool
	url: str
	target_dir: Path
	temp_dir: Path
	cookie_file: Optional[Path]
	archive_file: Optional[Path]
	indexes: Optional[str]

	tracks: list[Track]
	downloaded_files: list[Path]

	def __init__(self, normalize_only: bool,
			download_only: bool,
			url: str,
			target_dir: Path,
			cookie_file: Optional[Path],
			archive_file: Optional[Path],
			indexes: Optional[str]):
		
		self.normalize_only = normalize_only
		self.download_only = download_only
		self.url = url
		self.target_dir = target_dir
		self.temp_dir = target_dir / "tmp"
		self.cookie_file = cookie_file
		self.archive_file = archive_file
		self.indexes = indexes
		
		self.state = InitState(self)

		self.tracks = []
		self.downloaded_files= []

	def addTrack(self, tracks: list[Track]):
		self.tracks += tracks

	def addDownloadedFiles(self, files: list[Path]):
		self.downloaded_files += files

	def changeState(self, state: State):
		print(f"\033[91mChanging State to: {state.__class__.__name__}\033[0m")
		self.state = state

	def execute(self):
		self.state.execute()
