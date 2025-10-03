import subprocess
from pathlib import Path

def normalize_audio(file_path: Path) -> None:
    if not file_path.isfile():
        print(f"⚠️ File '{file_path}' not found, skipping normalization.")
        return

    normalized_file = file_path.with_name(f"normalized_{file_path.stem}.flac")

    print(f"🔊 Normalizing loudness: {file_path.name}\n")

    result = subprocess.run([
        "ffmpeg", 
        "-y", 
        "-i", str(file_path),
        "-filter:a", "loudnorm=I=-14:TP=-1.5:LRA=11", # Apply the loudness normalization filter
        "-map", "a", # Only include the audio stream
        "-map_metadata", "-1", # Remove all metadata 
        str(normalize_file)
    ], capture_output=True)
    
    if result.returncode == 0:
        print(f"✅ Loudness normalization successful for '{file_path.name}'.\n")
        try:
            file_path.unlink()
            normalized_file.rename(file_path)
        except Exception as e:
            print(f"⚠️ Failed to replace original file: {e}")
    else:
        print(f"❌ Loudness normalization failed for '{file_path.name}'.\n")
