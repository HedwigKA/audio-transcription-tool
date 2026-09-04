"""
Reformat Tool — Proses ulang transkrip yang sudah ada.
Membaca file SRT yang sudah ada dan menerapkan paragraph mode + topic segmentation
tanpa perlu melakukan transkripsi ulang.

Penggunaan:
    python reformat.py <file_srt> [opsi]

Contoh:
    python reformat.py "transcripts/Metopen 1.srt"
    python reformat.py "transcripts/Metopen 1.srt" --topics
    python reformat.py "transcripts/Metopen 1.srt" --gap 2.0 --topics
"""

import argparse
import os
import re
import sys

# Fix encoding untuk Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from transcriber.utils import (
    ensure_output_dir,
    format_duration,
    count_words,
    estimate_reading_time,
    print_banner,
)
from transcriber.formatter import merge_to_paragraphs, get_language_name


def parse_srt(file_path: str) -> list:
    """
    Parse file SRT menjadi list of segments.
    
    Args:
        file_path: Path ke file .srt
        
    Returns:
        List segmen, masing-masing berisi: id, start, end, text
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    segments = []
    # Pattern SRT: nomor, timestamp --> timestamp, teks
    pattern = re.compile(
        r"(\d+)\s*\n"
        r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n"
        r"((?:(?!\d+\s*\n\d{2}:\d{2}:\d{2}).)+)",
        re.MULTILINE,
    )
    
    for match in pattern.finditer(content):
        seg_id = int(match.group(1))
        start = srt_time_to_seconds(match.group(2))
        end = srt_time_to_seconds(match.group(3))
        text = match.group(4).strip().replace("\n", " ")
        
        if text:
            segments.append({
                "id": seg_id,
                "start": start,
                "end": end,
                "text": text,
            })
    
    return segments


def srt_time_to_seconds(time_str: str) -> float:
    """Convert SRT timestamp (HH:MM:SS,mmm) to seconds."""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def save_paragraph_txt(paragraphs: list, output_path: str, metadata: dict) -> str:
    """Simpan paragraf sebagai file TXT."""
    full_text = " ".join(p["text"] for p in paragraphs)
    word_count = count_words(full_text)
    reading_time = estimate_reading_time(word_count)
    
    lines = []
    lines.append("=" * 60)
    lines.append("  TRANSKRIP AUDIO (Reformatted)")
    lines.append(f"  Sumber        : {metadata.get('source', 'N/A')}")
    lines.append(f"  Durasi Audio  : {format_duration(metadata.get('duration', 0))}")
    lines.append(f"  Jumlah Kata   : {word_count:,} kata")
    lines.append(f"  Estimasi Baca : ~{reading_time} menit")
    lines.append(f"  Mode          : paragraph (gap={metadata.get('gap', 1.5)}s)")
    lines.append("=" * 60)
    lines.append("")
    lines.append("")
    
    for para in paragraphs:
        start_ts = format_duration(para["start"])
        end_ts = format_duration(para["end"])
        lines.append(f"[{start_ts} - {end_ts}]")
        lines.append(para["text"])
        lines.append("")
    
    content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def save_topics_txt(topics: list, output_path: str, metadata: dict) -> str:
    """Simpan topik sebagai file TXT."""
    all_text = " ".join(t["content"] for t in topics)
    word_count = count_words(all_text)
    reading_time = estimate_reading_time(word_count)
    
    lines = []
    lines.append("=" * 60)
    lines.append("  TRANSKRIP AUDIO (By Topics)")
    lines.append(f"  Sumber        : {metadata.get('source', 'N/A')}")
    lines.append(f"  Durasi Audio  : {format_duration(metadata.get('duration', 0))}")
    lines.append(f"  Jumlah Kata   : {word_count:,} kata")
    lines.append(f"  Estimasi Baca : ~{reading_time} menit")
    lines.append(f"  Topik         : {len(topics)} topik")
    lines.append(f"  Mode          : topics (Gemini AI)")
    lines.append("=" * 60)
    lines.append("")
    lines.append("")
    
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
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def create_parser() -> argparse.ArgumentParser:
    """Buat argument parser."""
    parser = argparse.ArgumentParser(
        prog="reformat",
        description="📋 Reformat Tool — Proses ulang transkrip SRT yang sudah ada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python reformat.py "transcripts/Metopen 1.srt"
  python reformat.py "transcripts/Metopen 1.srt" --topics
  python reformat.py "transcripts/Metopen 1.srt" --gap 2.0
  python reformat.py "transcripts/Metopen 1.srt" --topics --api-key AIzaSy...
        """,
    )
    
    parser.add_argument(
        "srt_file",
        type=str,
        help="Path ke file SRT yang sudah ada",
    )
    
    parser.add_argument(
        "--gap",
        type=float,
        default=1.5,
        help="Jeda minimum (detik) untuk paragraf baru (default: 1.5)",
    )
    
    parser.add_argument(
        "--topics", "-t",
        action="store_true",
        help="Aktifkan pengelompokan topik otomatis menggunakan Gemini AI",
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Google Gemini API key. Atau set env variable GEMINI_API_KEY",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Direktori output. Default: folder yang sama dengan file SRT",
    )
    
    return parser


def main():
    """Fungsi utama."""
    parser = create_parser()
    args = parser.parse_args()
    
    print_banner()
    
    # === Validasi file SRT ===
    srt_path = os.path.abspath(args.srt_file)
    if not os.path.exists(srt_path):
        print(f"❌ File tidak ditemukan: {srt_path}")
        sys.exit(1)
    
    if not srt_path.lower().endswith(".srt"):
        print(f"❌ File harus berformat .srt")
        sys.exit(1)
    
    srt_filename = os.path.basename(srt_path)
    srt_basename = os.path.splitext(srt_filename)[0]
    
    print(f"📄 File SRT: {srt_filename}")
    print(f"   Path: {srt_path}")
    
    # === Parse SRT ===
    print(f"\n🔍 Membaca file SRT...")
    segments = parse_srt(srt_path)
    
    if not segments:
        print(f"❌ Tidak ada segmen yang ditemukan di file SRT")
        sys.exit(1)
    
    duration = segments[-1]["end"] if segments else 0
    full_text = " ".join(s["text"] for s in segments)
    word_count = count_words(full_text)
    
    print(f"   ✅ {len(segments)} segmen ditemukan")
    print(f"   Durasi: {format_duration(duration)}")
    print(f"   Kata  : {word_count:,}")
    
    # === Setup output ===
    if args.output:
        output_dir = ensure_output_dir(args.output)
    else:
        output_dir = os.path.dirname(srt_path) or "."
    
    # === Merge ke paragraf ===
    print(f"\n📝 Menggabungkan segmen ke paragraf (gap={args.gap}s)...")
    paragraphs = merge_to_paragraphs(segments, args.gap)
    print(f"   ✅ {len(paragraphs)} paragraf terbentuk")
    
    metadata = {
        "source": srt_filename,
        "duration": duration,
        "gap": args.gap,
    }
    
    saved_files = []
    
    # Simpan versi paragraf
    para_path = os.path.join(output_dir, f"{srt_basename}_paragraph.txt")
    saved = save_paragraph_txt(paragraphs, para_path, metadata)
    saved_files.append(saved)
    
    # === Topic segmentation (jika diminta) ===
    if args.topics:
        print(f"\n" + "─" * 50)
        print("  ANALISIS TOPIK")
        print("─" * 50)
        
        try:
            from transcriber.topic_analyzer import get_api_key, analyze_topics
            
            api_key = get_api_key(args.api_key)
            topics = analyze_topics(paragraphs, api_key, language="id")
            
            if topics:
                topic_path = os.path.join(output_dir, f"{srt_basename}_topics.txt")
                saved = save_topics_txt(topics, topic_path, metadata)
                saved_files.append(saved)
        except ValueError as e:
            print(f"\n❌ {e}")
            sys.exit(1)
        except ImportError:
            print(f"\n❌ Library 'google-genai' belum terinstall!")
            print(f"   Jalankan: pip install google-genai")
            sys.exit(1)
        except Exception as e:
            print(f"\n⚠️  Error saat analisis topik: {e}")
    
    # === Ringkasan ===
    print(f"\n" + "=" * 50)
    print("  ✅ REFORMAT BERHASIL!")
    print("=" * 50)
    for f in saved_files:
        print(f"   💾 {f}")
    print("=" * 50)
    print()


if __name__ == "__main__":
    main()
