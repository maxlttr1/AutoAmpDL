from State import State
from NormalizeState import NormalizeState
from CheckState import CheckState

from pathlib import Path
import subprocess

class DownloadState(State):
	def __init__(self, context):
		self.context = context

	def execute(self):
		self.context.temp_dir.mkdir(exist_ok=True)
		self.context.addDownloadedFiles(download_playlist(
			self.context.url,
			self.context.cookie_file,
			self.context.temp_dir,
			self.context.indexes,
			self.context.archive_file
		))

		if self.context.download_only:
			self.context.changeState(CheckState(self.context))
		else:
			self.context.changeState(NormalizeState(self.context))

		self.context.execute()	

def download_playlist(url : str, cookies_file: Path, target_dir: Path, indexes: str | None, archive_file: Path) -> list[Path]:
    print(f"⬇️ Starting download of the playlist: {url} ...")

    output_template = str(target_dir / "%(title)s [%(id)s].%(ext)s")

    try:
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-quality", "0",
            "--audio-format", "flac",
            "--restrict-filenames",
            "-o", output_template,
            url
        ]

        if cookies_file:
            cmd.extend(["--cookies", str(cookies_file)])

        if archive_file:
            cmd.extend(["--download-archive", str(archive_file)])

        if indexes:
            cmd.extend(["--playlist-items", indexes])
        
        result = subprocess.run(cmd)

    except subprocess.TimeoutExpired:
        raise RuntimeError("❌ Download timed out")
    except Exception:
        raise RuntimeError("❌ Unexpected error during download")

    print(f"\033[32m✅ Download completed for {url}\033[0m")

    return [file for file in target_dir.iterdir() if file.is_file()]