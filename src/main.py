from pathlib import Path
from Context import Context
from FetchState import FetchState

import shutil
import sys
import argparse

def check_dependencies() -> None:
    if shutil.which("ffmpeg") is None:
        print("❌ ffmpeg is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)
    if shutil.which("yt-dlp") is None:
        print("❌ yt-dlp is not installed or not in PATH. Please install it before running this script.")
        sys.exit(1)

def arg_parser() -> tuple[bool, bool, str, Path, Path | None, Path | None, str | None]:
    parser = argparse.ArgumentParser(description="AutoAmpDL",
        epilog = """Examples:
    
    # Download a playlist and normalize the audio
    python main.py --url "https://www.youtube.com/playlist?list=PL..." ./output_dir

    # Download only (no normalization)
    python main.py --url "https://www.youtube.com/playlist?list=PL..." --download-only ./output_dir

    # Normalize only (existing files in a directory)
    python main.py --normalize-only ./output_dir

    # Download a specific range of tracks (e.g., tracks 10 to 20)
    python main.py --url "https://www.youtube.com/playlist?list=PL..." --start 10 --end 20 ./output_dir

    # Use cookies for downloading (e.g., for age-restricted content)
    python main.py --url "https://www.youtube.com/playlist?list=PL..." --cookies cookies.txt ./output_dir

    # Use a download archive to skip already downloaded videos
    python main.py --url "https://www.youtube.com/playlist?list=PL..." --download-archive ids.txt ./output_dir

    # Use a download archive AND download only a specific range
    python main.py --url "https://www.youtube.com/playlist?list=PL..." --download-archive ids.txt --start 5 --end 15 ./output_dir
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
    
    return (
        args.normalize_only, 
        args.download_only, 
        args.url or "", 
        target_dir,
        cookie_file,
        archive_file,
        indexes
    ) 

def main():
    check_dependencies()

    try:
        normalize_only, download_only, url, target_dir, cookie_file, archive_file, indexes = arg_parser()

        context = Context(
            normalize_only=normalize_only,
            download_only=download_only,
            url=url,
            target_dir=target_dir,
            cookie_file=cookie_file,
            archive_file=archive_file,
            indexes=indexes
        )
        
        context.execute()

    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C).")
        return

if __name__ == "__main__":
    main()
