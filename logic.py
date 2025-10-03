import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

from downloader import fetch_playlist, download_track
from normalizer import normalize_audio

def arg_parser() -> None:
    parser = argparse.ArgumentParser(description="AutoAmpDL")

    # Exclusion for --url and --normalize-only
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL to download from (playlist or a single audio/video)')
    group.add_argument('--normalize-only', action='store_true', help='Run normalize-only mode')

    parser.add_argument('directory', nargs='?', default='.', help='Directory to save the download (default: current directory)')

    args = parser.parse_args()
    target_dir = Path(args.directory).resolve()

    if not(target_dir.is_dir()):
        print(f"{args.directory} not found. Please provide a correct directory")
        sys.exit(1)

    launch_processes(args.normalize_only, target_dir, args.url)

def launch_processes(normalize_only: bool, target_dir: Path, url: str | None) -> None:
    if normalize_only:
        files = list(target_dir.glob("*.flac"))
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

        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Downloading tracks...", total=len(tracks))

            with ProcessPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(download_track, track, Path("./cookies.txt"), temp_dir): track for track in tracks}
                downloaded_files = []
                for future in as_completed(futures):
                    progress.update(task, advance=1)
                    try:
                        downloaded_files.append(future.result())
                    except Exception as e:
                        print(f"Error during download: {e}")

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

        # Move files from tmp to target directory
        for file in downloaded_files:
            target = target_dir / file.name
            file.rename(target)

        try:
            temp_dir.rmdir()
            print("Temporary directory removed successfully.")
        except Exception as e:
            print(f"Failed to remove temporary directory: {e}")

def check_missing_tracks(tracks: list[Track], downloaded_files: list[Path]) -> list[Track]:
    downloaded_names = {file.stem for file in downloaded_files}
    missing_tracks = []

    for track in tracks:
        # Assuming Track has a 'filename' attribute which matches the saved filename
        if f"{track.filename} [{track.video_id}]" not in downloaded_names:
            missing_tracks.append(track)

    return missing_tracks
    

    