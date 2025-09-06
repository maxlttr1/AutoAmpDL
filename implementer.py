import os
import subprocess

def search_youtube(query):
    """Use yt-dlp to search YouTube and return the first video URL."""
    try:
        result = subprocess.run(
            ['yt-dlp', f"ytsearch1:{query}", '--get-id'],
            capture_output=True,
            text=True
        )
        video_id = result.stdout.strip()
        return f"https://www.youtube.com/watch?v={video_id}" if video_id else None
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return None

def build_playlist(directory, output_file='playlist.m3u'):
    #Search YouTube for all audio files in a folder and write the matches to a playlist.
    supported_exts = ('.mp3', '.flac', '.wav', '.m4a', '.aac')
    entries = []

    for file in os.listdir(directory):
        if file.lower().endswith(supported_exts):
            title = os.path.splitext(file)[0]  # remove extension
            print(f"🔍 Searching for: {title}")
            url = search_youtube(f"{title} official audio")
            if url:
                print(f"✅ Found: {url}")
                entries.append(url)
            else:
                print(f"❌ No match found for: {title}")

    # Save playlist
    with open(output_file, 'w') as f:
        f.write("#EXTM3U\n")
        for url in entries:
            f.write(url + '\n')

    print(f"\n🎧 Playlist saved to {output_file} with {len(entries)} entries.")

# === Usage ===
if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    build_playlist(directory)
