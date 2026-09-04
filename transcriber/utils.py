"""
Utility functions untuk audio transcription tool.
Berisi helper untuk validasi file, format waktu, dan pengecekan sistem.
"""

import os
import shutil
import subprocess
import sys


# Format audio yang didukung oleh Whisper/FFmpeg
SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4", ".wma", ".aac"}


def validate_audio_file(file_path: str) -> str:
    """
    Validasi file audio: cek keberadaan file dan format yang didukung.
    
    Args:
        file_path: Path ke file audio
        
    Returns:
        Absolute path ke file audio yang sudah divalidasi
        
    Raises:
        FileNotFoundError: Jika file tidak ditemukan
        ValueError: Jika format file tidak didukung
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File tidak ditemukan: {abs_path}")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path bukan file: {abs_path}")
    
    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(
            f"Format '{ext}' tidak didukung.\n"
            f"Format yang didukung: {supported}"
        )
    
    return abs_path


def format_duration(seconds: float) -> str:
    """
    Format durasi dari detik ke format HH:MM:SS.
    
    Args:
        seconds: Durasi dalam detik
        
    Returns:
        String format "HH:MM:SS"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp untuk tampilan di transkrip.
    
    Args:
        seconds: Waktu dalam detik
        
    Returns:
        String format "[HH:MM:SS]"
    """
    return f"[{format_duration(seconds)}]"


def format_srt_timestamp(seconds: float) -> str:
    """
    Format timestamp untuk file SRT (SubRip Subtitle).
    
    Args:
        seconds: Waktu dalam detik
        
    Returns:
        String format "HH:MM:SS,mmm"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def estimate_reading_time(word_count: int, wpm: int = 200) -> int:
    """
    Estimasi waktu baca dalam menit.
    Rata-rata kecepatan baca: 200 kata per menit.
    
    Args:
        word_count: Jumlah kata
        wpm: Kata per menit (default 200)
        
    Returns:
        Estimasi waktu baca dalam menit
    """
    return max(1, round(word_count / wpm))


def count_words(text: str) -> int:
    """Hitung jumlah kata dalam teks."""
    return len(text.split())


def check_ffmpeg() -> bool:
    """
    Cek apakah FFmpeg sudah terinstall di sistem.
    
    Returns:
        True jika FFmpeg ditemukan, False jika tidak
    """
    if shutil.which("ffmpeg") is not None:
        return True
    
    # Coba jalankan ffmpeg langsung
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return True
    except (FileNotFoundError, OSError):
        return False


def check_cuda() -> bool:
    """
    Cek apakah CUDA (GPU NVIDIA) tersedia untuk akselerasi.
    
    Returns:
        True jika CUDA tersedia, False jika tidak
    """
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_device_info() -> dict:
    """
    Dapatkan informasi device yang akan digunakan.
    
    Returns:
        Dict berisi informasi device (name, type, vram)
    """
    info = {"type": "cpu", "name": "CPU"}
    
    try:
        import torch
        if torch.cuda.is_available():
            info["type"] = "cuda"
            info["name"] = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            vram_bytes = getattr(props, "total_memory", None) or getattr(props, "total_mem", 0)
            info["vram_gb"] = round(vram_bytes / (1024 ** 3), 1)
    except ImportError:
        pass
    
    return info


def ensure_output_dir(output_dir: str) -> str:
    """
    Pastikan direktori output ada. Buat jika belum ada.
    
    Args:
        output_dir: Path ke direktori output
        
    Returns:
        Absolute path ke direktori output
    """
    abs_dir = os.path.abspath(output_dir)
    os.makedirs(abs_dir, exist_ok=True)
    return abs_dir


def get_model_info() -> dict:
    """
    Informasi tentang model Whisper yang tersedia.
    
    Returns:
        Dict model_name -> {size, vram, description}
    """
    return {
        "tiny": {
            "size": "~75 MB",
            "vram": "~1 GB",
            "description": "Tercepat, akurasi rendah. Cocok untuk tes cepat.",
        },
        "base": {
            "size": "~145 MB",
            "vram": "~1 GB",
            "description": "Cepat, akurasi cukup. Cocok untuk audio jelas.",
        },
        "small": {
            "size": "~470 MB",
            "vram": "~2 GB",
            "description": "Balance kecepatan & akurasi. Recommended untuk RTX 3050.",
        },
        "medium": {
            "size": "~1.5 GB",
            "vram": "~5 GB",
            "description": "Akurasi tinggi. Mungkin perlu fallback ke CPU di RTX 3050.",
        },
        "large-v3": {
            "size": "~3 GB",
            "vram": "~10 GB",
            "description": "Paling akurat. Jalan di CPU untuk GPU < 10 GB VRAM.",
        },
    }


def safe_print(text: str):
    """Print teks dengan handling untuk karakter Unicode di Windows console."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: ganti karakter yang tidak bisa di-encode
        print(text.encode("ascii", errors="replace").decode("ascii"))


def print_banner():
    """Tampilkan banner aplikasi."""
    banner = """
+==================================================+
|       AUDIO TRANSCRIPTION TOOL                   |
|       Transkrip Rekaman Audio ke Teks            |
|       Powered by OpenAI Whisper                  |
+==================================================+
    """
    safe_print(banner)
