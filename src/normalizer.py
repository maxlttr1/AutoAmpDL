import subprocess
import json
from pathlib import Path

def analyse_loudness(file_path: Path) -> dict:
    cmd = [
        "ffmpeg",
        "-i", str(file_path),
        "-af", "loudnorm=I=-14:TP=-1:LRA=14:print_format=json",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    json_str = ""
    in_json = False
    for line in stderr.splitlines():
        if line.strip() == "{":
            in_json = True
            json_str = line
        elif in_json:
            json_str += "\n" + line
            if line.strip() == "}":
                break

    if not json_str:
        raise RuntimeError("Could not find loudnorm JSON output")

    return json.loads(json_str)

def normalize_audio(file_path: Path) -> None:
    if not file_path.is_file():
        print(f"⚠️ File '{file_path}' not found, skipping normalization.")
        return
    
    normalized_file = file_path.with_name(f"normalized_{file_path.stem}.flac")

    stats = analyse_loudness(file_path)

    input_i = stats["input_i"]
    input_tp = stats["input_tp"]
    input_lra = stats["input_lra"]
    input_thresh = stats["input_thresh"]
    offset = stats["target_offset"]

    cmd = [
        "ffmpeg", 
        "-y", 
        "-i", str(file_path),
        "-af", (
            f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={input_i}:measured_TP={input_tp}:"
            f"measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={offset}"
        ), # Apply the loudness normalization filter
        "-map", "a", # Only include the audio stream
        "-map_metadata", "-1", # Remove all metadata 
        str(normalized_file)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Loudness normalization successful for '{file_path.name}'.")
        try:
            file_path.unlink()
            normalized_file.rename(file_path.with_suffix(".flac"))
        except Exception as e:
            print(f"⚠️ Failed to replace original file: {e}")
    else:
        print(f"❌ Loudness normalization failed for '{file_path.name}'.")