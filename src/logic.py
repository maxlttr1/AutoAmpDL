import argparse
import sys

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

from downloader import fetch_playlist, download_playlist
from normalizer import normalize_audio
from check import check_missing_tracks

def arg_parser() -> None:
    parser = argparse.ArgumentParser(description="AutoAmpDL",
        epilog = """Examples:
    
    # Download a playlist and normalize the audio
    python script.py --url "https://www.youtube.com/playlist?list=PL..." ./output_dir

    # Download only (no normalization)
    python script.py --url "https://www.youtube.com/playlist?list=PL..." --download-only ./output_dir

    # Normalize only (existing files in a directory)
    python script.py --normalize-only ./output_dir

    # Download a specific range of tracks (e.g., tracks 10 to 20)
    python script.py --url "https://www.youtube.com/playlist?list=PL..." --start 10 --end 20 ./output_dir

    # Use cookies for downloading (e.g., for age-restricted content)
    python script.py --url "https://www.youtube.com/playlist?list=PL..." --cookies cookies.txt ./output_dir

    # Use a download archive to skip already downloaded videos
    python script.py --url "https://www.youtube.com/playlist?list=PL..." --download-archive ids.txt ./output_dir

    # Use a download archive AND download only a specific range
    python script.py --url "https://www.youtube.com/playlist?list=PL..." --download-archive ids.txt --start 5 --end 15 ./output_dir
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Exclusion for --url and --normalize-only
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL to download from (playlist or a single audio/video)')
    group.add_argument('--normalize-only', action='store_true', help='Run normalize-only mode')

    parser.add_argument('--download-only', action='store_true', help='Run download-only mode')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to save the download (default: current directory)')
    parser.add_argument('--cookies', help='Cookie file to provide to yt-dlp (for age restricted content or rate limiting)')
    parser.add_argument('--start', type=int, help='Where to start the downloading the playlist from')
    parser.add_argument('--end', type=int, help='Where to end downloading the playlist')
    parser.add_argument('--download-archive', help='Checks whether a video has already been downloaded.')

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

    archive_file = ""
    if args.download_archive:
        archive_file = Path(args.download_archive).resolve()
        if not(archive_file.is_file()):
            print(f"{args.download_archive} not found. Please provide a correct file")
            sys.exit(1)

    launch_processes(normalize_only=args.normalize_only, download_only=args.download_only, target_dir=target_dir, url=args.url, cookie_file=cookie_file, indexes=indexes, archive_file=archive_file)

def launch_processes(normalize_only: bool, download_only: bool, target_dir: Path, url: str | None, cookie_file: Path, indexes: str | None, archive_file: Path) -> None:
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
            for file in files:
                normalize_audio(file)
                progress.update(task, advance=1)
            """task = progress.add_task("Normalizing tracks...", total=len(files))

            with ProcessPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(normalize_audio, file): file for file in files}
                for _ in as_completed(futures):
                    progress.update(task, advance=1)"""
        
                    
    else:
        tracks = fetch_playlist(url=url, indexes=indexes, archive_file=archive_file)
        temp_dir = target_dir / "tmp"
        temp_dir.mkdir(exist_ok=True)

        downloaded_files = download_playlist(url=url, cookies_path=cookie_file, target_dir=temp_dir, indexes=indexes, archive_file=archive_file)

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

                with ProcessPoolExecutor(max_workers=5) as executor:
                    futures = {executor.submit(normalize_audio, file): file for file in downloaded_files}
                    for _ in as_completed(futures):
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
    

    