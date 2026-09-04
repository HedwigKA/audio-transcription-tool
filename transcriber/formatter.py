"""
Output formatter module.
Mengformat hasil transkripsi ke berbagai format output (TXT, SRT).
Mendukung mode paragraf (menggabungkan segmen berdasarkan jeda bicara).
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


def merge_to_paragraphs(segments: list, gap_threshold: float = 1.5) -> list:
    """
    Gabungkan segmen-segmen Whisper menjadi paragraf berdasarkan jeda bicara.
    
    Jika jeda antar segmen kurang dari gap_threshold, segmen digabung
    ke paragraf yang sama. Jika jeda >= gap_threshold, paragraf baru dimulai.
    
    Args:
        segments: List segmen dari Whisper (masing-masing punya start, end, text)
        gap_threshold: Jeda minimum (detik) untuk memulai paragraf baru. Default: 1.5
        
    Returns:
        List paragraf, masing-masing berisi:
        - "start": Waktu mulai paragraf
        - "end": Waktu akhir paragraf
        - "text": Teks gabungan paragraf
    """
    if not segments:
        return []
    
    paragraphs = []
    current_paragraph = {
        "start": segments[0]["start"],
        "end": segments[0]["end"],
        "texts": [segments[0]["text"]],
    }
    
    for i in range(1, len(segments)):
        prev_end = segments[i - 1]["end"]
        curr_start = segments[i]["start"]
        gap = curr_start - prev_end
        
        if gap >= gap_threshold:
            # Jeda cukup lama -> paragraf baru
            current_paragraph["text"] = " ".join(
                t for t in current_paragraph["texts"] if t.strip()
            )
            if current_paragraph["text"].strip():
                paragraphs.append({
                    "start": current_paragraph["start"],
                    "end": current_paragraph["end"],
                    "text": current_paragraph["text"].strip(),
                })
            
            # Mulai paragraf baru
            current_paragraph = {
                "start": segments[i]["start"],
                "end": segments[i]["end"],
                "texts": [segments[i]["text"]],
            }
        else:
            # Jeda pendek -> gabung ke paragraf yang sama
            current_paragraph["end"] = segments[i]["end"]
            current_paragraph["texts"].append(segments[i]["text"])
    
    # Tambahkan paragraf terakhir
    current_paragraph["text"] = " ".join(
        t for t in current_paragraph["texts"] if t.strip()
    )
    if current_paragraph["text"].strip():
        paragraphs.append({
            "start": current_paragraph["start"],
            "end": current_paragraph["end"],
            "text": current_paragraph["text"].strip(),
        })
    
    return paragraphs


def _build_header(result: dict, mode: str = "paragraph") -> list:
    """Bangun header untuk file output TXT."""
    full_text = result["text"]
    word_count = count_words(full_text)
    reading_time = estimate_reading_time(word_count)
    language_name = get_language_name(result["language"])
    
    lines = []
    lines.append("=" * 60)
    lines.append("  TRANSKRIP AUDIO")
    lines.append(f"  Durasi Audio  : {format_duration(result['duration'])}")
    lines.append(f"  Jumlah Kata   : {word_count:,} kata")
    lines.append(f"  Estimasi Baca : ~{reading_time} menit")
    lines.append(f"  Model         : {result['model']}")
    lines.append(f"  Bahasa        : {language_name} (auto-detected)")
    lines.append(f"  Device        : {result['device'].upper()}")
    lines.append(f"  Waktu Proses  : {format_duration(result['processing_time'])}")
    lines.append(f"  Mode          : {mode}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("")
    return lines


def to_txt(result: dict, output_path: str, paragraph_mode: bool = True,
           gap_threshold: float = 1.5) -> str:
    """
    Format hasil transkripsi sebagai file TXT.
    
    Args:
        result: Dict hasil dari transcribe_audio()
        output_path: Path untuk menyimpan file .txt
        paragraph_mode: Jika True, gabungkan segmen menjadi paragraf
        gap_threshold: Jeda minimum untuk paragraf baru (detik)
        
    Returns:
        Path file yang berhasil disimpan
    """
    segments = result["segments"]
    
    # Bangun header
    mode_label = f"paragraph (gap={gap_threshold}s)" if paragraph_mode else "segment"
    lines = _build_header(result, mode=mode_label)
    
    if paragraph_mode:
        # Mode paragraf: gabungkan segmen berdasarkan jeda
        paragraphs = merge_to_paragraphs(segments, gap_threshold)
        for para in paragraphs:
            start_ts = format_duration(para["start"])
            end_ts = format_duration(para["end"])
            lines.append(f"[{start_ts} - {end_ts}]")
            lines.append(para["text"])
            lines.append("")
    else:
        # Mode segmen: format lama (per segmen)
        for segment in segments:
            timestamp = format_timestamp(segment["start"])
            text = segment["text"]
            if text:
                lines.append(f"{timestamp} {text}")
                lines.append("")
    
    # Tulis ke file
    content = "\n".join(lines)
    
    if not output_path.lower().endswith(".txt"):
        output_path += ".txt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def to_txt_topics(result: dict, topics: list, output_path: str) -> str:
    """
    Format hasil transkripsi sebagai file TXT yang dikelompokkan per topik.
    
    Args:
        result: Dict hasil dari transcribe_audio()
        topics: List topik dari topic_analyzer, masing-masing berisi:
                - "title": Judul topik
                - "start": Waktu mulai
                - "end": Waktu akhir
                - "content": Teks isi topik
        output_path: Path untuk menyimpan file .txt
        
    Returns:
        Path file yang berhasil disimpan
    """
    # Bangun header
    lines = _build_header(result, mode="topics (Gemini AI)")
    
    for i, topic in enumerate(topics, 1):
        lines.append("=" * 60)
        lines.append(f"  TOPIK {i}: {topic['title']}")
        if topic.get("start") is not None and topic.get("end") is not None:
            lines.append(f"  Waktu: {format_duration(topic['start'])} - {format_duration(topic['end'])}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(topic["content"])
        lines.append("")
        lines.append("")
    
    content = "\n".join(lines)
    
    if not output_path.lower().endswith(".txt"):
        output_path += ".txt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def to_srt(result: dict, output_path: str) -> str:
    """
    Format hasil transkripsi sebagai file SRT (SubRip Subtitle).
    
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
        
        if text:
            lines.append(str(i))
            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")
    
    content = "\n".join(lines)
    
    if not output_path.lower().endswith(".srt"):
        output_path += ".srt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def save_output(result: dict, output_dir: str, base_name: str, formats: list,
                paragraph_mode: bool = True, gap_threshold: float = 1.5,
                topics: list = None) -> list:
    """
    Simpan hasil transkripsi ke berbagai format.
    
    Args:
        result: Dict hasil dari transcribe_audio()
        output_dir: Direktori output
        base_name: Nama dasar file (tanpa ekstensi)
        formats: List format yang diinginkan ("txt", "srt")
        paragraph_mode: Gunakan mode paragraf untuk TXT
        gap_threshold: Jeda minimum untuk paragraf baru
        topics: List topik dari topic_analyzer (jika ada)
        
    Returns:
        List path file yang berhasil disimpan
    """
    saved_files = []
    
    for fmt in formats:
        output_path = os.path.join(output_dir, f"{base_name}.{fmt}")
        
        if fmt == "txt":
            if topics:
                # Mode topik: simpan versi topik
                topic_path = os.path.join(output_dir, f"{base_name}_topics.txt")
                saved = to_txt_topics(result, topics, topic_path)
                saved_files.append(saved)
                # Juga simpan versi paragraf biasa
                saved = to_txt(result, output_path, paragraph_mode, gap_threshold)
                saved_files.append(saved)
            else:
                saved = to_txt(result, output_path, paragraph_mode, gap_threshold)
                saved_files.append(saved)
        elif fmt == "srt":
            saved = to_srt(result, output_path)
            saved_files.append(saved)
        else:
            print(f"⚠️  Format '{fmt}' tidak dikenal, dilewati.")
    
    return saved_files
