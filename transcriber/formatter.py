"""
Output formatter module.
Mengformat hasil transkripsi ke berbagai format output (TXT, SRT).
"""

import os

from .utils import (
    format_timestamp,
    format_srt_timestamp,
    format_duration,
    count_words,
    estimate_reading_time,
)


# Mapping kode bahasa ke nama lengkap
LANGUAGE_NAMES = {
    "id": "Indonesian",
    "en": "English",
    "jv": "Javanese",
    "su": "Sundanese",
    "ms": "Malay",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
    "nl": "Dutch",
    "th": "Thai",
    "vi": "Vietnamese",
}


def get_language_name(code: str) -> str:
    """Dapatkan nama lengkap bahasa dari kode bahasa."""
    return LANGUAGE_NAMES.get(code, code.capitalize())


def to_txt(result: dict, output_path: str) -> str:
    """
    Format hasil transkripsi sebagai file TXT dengan timestamp dan ringkasan.
    
    Args:
        result: Dict hasil dari transcribe_audio()
        output_path: Path untuk menyimpan file .txt
        
    Returns:
        Path file yang berhasil disimpan
    """
    segments = result["segments"]
    full_text = result["text"]
    
    # Hitung statistik
    word_count = count_words(full_text)
    reading_time = estimate_reading_time(word_count)
    language_name = get_language_name(result["language"])
    
    # Bangun header
    lines = []
    lines.append("═" * 60)
    lines.append("  TRANSKRIP AUDIO")
    lines.append(f"  Durasi Audio  : {format_duration(result['duration'])}")
    lines.append(f"  Jumlah Kata   : {word_count:,} kata")
    lines.append(f"  Estimasi Baca : ~{reading_time} menit")
    lines.append(f"  Model         : {result['model']}")
    lines.append(f"  Bahasa        : {language_name} (auto-detected)")
    lines.append(f"  Device        : {result['device'].upper()}")
    lines.append(f"  Waktu Proses  : {format_duration(result['processing_time'])}")
    lines.append("═" * 60)
    lines.append("")
    lines.append("")
    
    # Tulis setiap segmen dengan timestamp
    for segment in segments:
        timestamp = format_timestamp(segment["start"])
        text = segment["text"]
        if text:  # Skip segmen kosong
            lines.append(f"{timestamp} {text}")
            lines.append("")
    
    # Tulis ke file
    content = "\n".join(lines)
    
    # Pastikan path berakhiran .txt
    if not output_path.lower().endswith(".txt"):
        output_path += ".txt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def to_srt(result: dict, output_path: str) -> str:
    """
    Format hasil transkripsi sebagai file SRT (SubRip Subtitle).
    
    Format SRT standar:
    1
    00:00:15,000 --> 00:00:30,500
    Teks subtitle di sini
    
    Args:
        result: Dict hasil dari transcribe_audio()
        output_path: Path untuk menyimpan file .srt
        
    Returns:
        Path file yang berhasil disimpan
    """
    segments = result["segments"]
    
    lines = []
    for i, segment in enumerate(segments, 1):
        start = format_srt_timestamp(segment["start"])
        end = format_srt_timestamp(segment["end"])
        text = segment["text"]
        
        if text:  # Skip segmen kosong
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")  # Baris kosong sebagai pemisah
    
    # Tulis ke file
    content = "\n".join(lines)
    
    # Pastikan path berakhiran .srt
    if not output_path.lower().endswith(".srt"):
        output_path += ".srt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def save_output(result: dict, output_dir: str, base_name: str, formats: list) -> list:
    """
    Simpan hasil transkripsi ke berbagai format.
    
    Args:
        result: Dict hasil dari transcribe_audio()
        output_dir: Direktori output
        base_name: Nama dasar file (tanpa ekstensi)
        formats: List format yang diinginkan ("txt", "srt")
        
    Returns:
        List path file yang berhasil disimpan
    """
    saved_files = []
    
    for fmt in formats:
        output_path = os.path.join(output_dir, f"{base_name}.{fmt}")
        
        if fmt == "txt":
            saved = to_txt(result, output_path)
            saved_files.append(saved)
        elif fmt == "srt":
            saved = to_srt(result, output_path)
            saved_files.append(saved)
        else:
            print(f"⚠️  Format '{fmt}' tidak dikenal, dilewati.")
    
    return saved_files
