import subprocess
from pathlib import Path

def capture_frame(video_path, timestamp, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path, "-vframes", "1", "-q:v", "2", output_path], check=True, capture_output=True)
    return output_path

def capture_section_frames(video_path, sections, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    frames = {}
    for section in sections:
        section_id = section["id"]
        timestamp = section["start_time"]
        frame_path = str(Path(output_dir) / f"{section_id}.jpg")
        try:
            capture_frame(video_path, timestamp, frame_path)
            frames[section_id] = frame_path
            print(f"  Frame capturado: {section_id} @ {timestamp}s -> {frame_path}")
        except subprocess.CalledProcessError as e:
            print(f"  ERROR capturando frame {section_id} @ {timestamp}s: {e}")
    return frames
