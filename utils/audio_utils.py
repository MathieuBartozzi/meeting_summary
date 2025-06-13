import os
import tempfile
import io
from pydub import AudioSegment

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

def split_audio(file_bytes, chunk_duration_minutes=30, original_filename="audio.webm"):
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        audio = AudioSegment.from_file(tmp.name)

    chunks = []
    chunk_length_ms = chunk_duration_minutes * 60 * 1000
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_io = io.BytesIO()
        chunk.export(chunk_io, format="webm")
        chunk_io.seek(0)
        chunk_io.name = safe_filename(original_filename, prefix=f"chunk_{i+1}")
        chunks.append(chunk_io)

    return chunks
