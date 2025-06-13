import os
import math
from pathlib import Path
from typing import List
import tempfile
import ffmpeg


def safe_filename(name: str, prefix: str = "audio") -> str:
    _, ext = os.path.splitext(name)
    ext = ext.lower()
    if ext not in [".webm", ".mp3", ".wav", ".mp4", ".ogg", ".flac", ".m4a"]:
        ext = ".webm"
    return f"{prefix}{ext}"



def split_audio(audio_bytes: bytes, original_filename: str, segment_duration_sec: int = 1800) -> List[Path]:
    """
    Découpe un fichier audio en segments de longueur donnée (en secondes) avec ffmpeg.
    Retourne une liste de fichiers temporaires (Path) contenant les segments.
    """
    ext = Path(original_filename).suffix.replace('.', '') or 'mp3'
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
    temp_input.write(audio_bytes)
    temp_input.flush()

    # Obtenir la durée totale
    probe = ffmpeg.probe(temp_input.name)
    total_duration = float(probe['format']['duration'])

    segments = []
    num_segments = math.ceil(total_duration / segment_duration_sec)

    for i in range(num_segments):
        start_time = i * segment_duration_sec
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
        ffmpeg.input(temp_input.name, ss=start_time, t=segment_duration_sec).output(temp_output.name, loglevel="quiet").run()
        segments.append(Path(temp_output.name))

    return segments
