import argparse
import sys
from pathlib import Path
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

    parser.add_argument('--download-only', action='store_true', help='Run download-only mode')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to save the download (default: current directory)')
    parser.add_argument('--cookies', help='Cookie file to provide to yt-dlp (for age restricted content or rate limiting)')
    parser.add_argument('--start', type=int, help='Where to start the downloading the playlist from')
    parser.add_argument('--end', type=int, help='Where to end downloading the playlist')

    args = parser.parse_args()
    target_dir = Path(args.directory).resolve()

    if not(target_dir.is_dir()):
        print(f"{args.directory} not found. Please provide a correct directory")
        sys.exit(1)

    cookie_file = ""
    if args.cookies:
        cookie_file = Path(args.cookies).resolve()
        if not(cookie_file.is_file()):
            print(f"{args.cookies} not found. Please provide a correct file")
            sys.exit(1)

    indexes = ""
    if args.start and args.end and args.start < args.end:
        indexes = f"{args.start}-{args.end}"
    elif args.start and args.end and args.start == args.end:
        indexes = f"{args.start}"
    elif args.start and not(args.end) and int(args.start) >= 1:
        indexes = f"{args.start}-"
    elif not(args.start) and args.end and int(args.end) > 1:
        indexes = f"1-{args.end}"
    elif not(args.start) and not(args.end):
        indexes = ""
    else:
        print(f"Index start: {args.start}, Index end: {args.end}. Please provide correct Index values")
        sys.exit(1)

    launch_processes(normalize_only=args.normalize_only, download_only=args.download_only, target_dir=target_dir, url=args.url, cookie_file=cookie_file, indexes=indexes)

def launch_processes(normalize_only: bool, download_only: bool, target_dir: Path, url: str | None, cookie_file: Path, indexes: str | None, logs) -> None:
    if normalize_only:
        files = [file for file in target_dir.iterdir() if file.is_file()]
        '''with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Normalizing tracks...", total=len(files))
            
            for file in files:
                normalize_audio(file)
                progress.update(task, advance=1)'''
        for index, file in enumerate(files):
            normalize_audio(file, logs)
            #updateBar(index + 1, len(files)) 
        
    else:
        tracks = fetch_playlist(url=url, indexes=indexes)
        temp_dir = target_dir / "tmp"
        temp_dir.mkdir(exist_ok=True)

        downloaded_files = download_playlist(url=url, cookies_path=cookie_file, target_dir=temp_dir, indexes=indexes)

        if downloaded_files and not(download_only):
            # Normalize downloaded files
            with Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Normalizing tracks...", total=len(downloaded_files))
                
                for file in downloaded_files:
                    normalize_audio(file)
                    progress.update(task, advance=1)

        check_missing_tracks(tracks=tracks, downloaded_files=downloaded_files)

        for file in downloaded_files:
            target = target_dir / file.name
            if target.exists():
                print(f"📣 {target} already exists! Not replacing it...")
                file.unlink()
            else:
                file.rename(target)

        try:
            temp_dir.rmdir()
            print("Temporary directory removed successfully.")
        except Exception as e:
            print(f"Failed to remove temporary directory: {e}")
    

    