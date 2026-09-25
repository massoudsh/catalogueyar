import subprocess
from pathlib import Path

from app.pipeline.errors import EngineCallError

VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}


def is_video(path: str) -> bool:
    return Path(path).suffix.lower() in VIDEO_SUFFIXES


def extract_video_frames(video_path: str, output_dir: str, max_frames: int = 5) -> list[str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    pattern = target / "frame-%02d.jpg"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        video_path,
        "-vf",
        f"fps=1,scale=1024:-1:force_original_aspect_ratio=decrease",
        "-frames:v",
        str(max_frames),
        str(pattern),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    except FileNotFoundError as exc:
        raise EngineCallError("ffmpeg برای پردازش ویدئو نصب نیست") from exc
    except subprocess.SubprocessError as exc:
        raise EngineCallError(f"خطا در استخراج فریم ویدئو: {exc}") from exc

    frames = sorted(str(path) for path in target.glob("frame-*.jpg"))
    if not frames:
        raise EngineCallError("هیچ فریمی از ویدئو استخراج نشد")
    return frames
