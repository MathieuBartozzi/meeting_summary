import os
import tempfile
import io
import math
import tempfile
from pathlib import Path
from typing import List
import ffmpeg


def safe_filename(name: str, prefix: str = "audio") -> str:
    _, ext = os.path.splitext(name)
    ext = ext.lower()
    if ext not in [".webm", ".mp3", ".wav", ".mp4", ".ogg", ".flac", ".m4a"]:
        ext = ".webm"
    return f"{prefix}{ext}"

def get_audio_duration(file_bytes):
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        audio = AudioSegment.from_file(tmp.name)
        return len(audio) / 1000 / 60  # minutes

# def split_audio(file_bytes, chunk_duration_minutes=30, original_filename="audio.webm"):
#     with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
#         tmp.write(file_bytes)
#         tmp.flush()
#         audio = AudioSegment.from_file(tmp.name)

#     chunks = []
#     chunk_length_ms = chunk_duration_minutes * 60 * 1000
#     for i in range(0, len(audio), chunk_length_ms):
#         chunk = audio[i:i+chunk_length_ms]
#         chunk_io = io.BytesIO()
#         chunk.export(chunk_io, format="webm")
#         chunk_io.seek(0)
#         chunk_io.name = safe_filename(original_filename, prefix=f"chunk_{i+1}")
#         chunks.append(chunk_io)

#     return chunks

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
