import argparse
import sys

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

from downloader import fetch_playlist, download_playlist
from normalizer import normalize_audio
from check import check_missing_tracks

def arg_parser() -> None:
    parser = argparse.ArgumentParser(description="AutoAmpDL")

    # Exclusion for --url and --normalize-only
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL to download from (playlist or a single audio/video)')
    group.add_argument('--normalize-only', action='store_true', help='Run normalize-only mode')

    parser.add_argument('directory', nargs='?', default='.', help='Directory to save the download (default: current directory)')
    parser.add_argument('--cookies', help='Cookie file to provide to yt-dlp (for age restricted content or rate limiting)')

    args = parser.parse_args()
    target_dir = Path(args.directory).resolve()

    if not(target_dir.is_dir()):
        print(f"{args.directory} not found. Please provide a correct directory")
        sys.exit(1)

    if args.cookies:
        cookie_file = Path(args.cookies).resolve()
        if not(cookie_file.is_file()):
            print(f"{args.cookies} not found. Please provide a correct file")
            sys.exit(1)

    launch_processes(args.normalize_only, target_dir, args.url)

def launch_processes(normalize_only: bool, target_dir: Path, url: str | None) -> None:
    if normalize_only:
        files = [file for file in target_dir.iterdir() if file.is_file()]
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Normalizing tracks...", total=len(files))

            with ProcessPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(normalize_audio, file): file for file in files}
                for _ in as_completed(futures):
                    progress.update(task, advance=1)
    else:
        tracks = fetch_playlist(url)
        temp_dir = target_dir / "tmp"
        temp_dir.mkdir(exist_ok=True)

        downloaded_files = download_playlist(url, Path("./cookies.txt"), temp_dir)

        # Normalize downloaded files
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Normalizing tracks...", total=len(downloaded_files))

            with ProcessPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(normalize_audio, file): file for file in downloaded_files}
                for _ in as_completed(futures):
                    progress.update(task, advance=1)

        check_missing_tracks(tracks, downloaded_files)

        for file in downloaded_files:
            target = target_dir / file.name
            file.rename(target)

        try:
            temp_dir.rmdir()
            print("Temporary directory removed successfully.")
        except Exception as e:
            print(f"Failed to remove temporary directory: {e}")
    

    