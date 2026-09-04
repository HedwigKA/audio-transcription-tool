"""
Audio Transcription Tool — CLI Entry Point
Transkrip rekaman audio kuliah menjadi teks menggunakan OpenAI Whisper.

Penggunaan:
    python transcribe.py <file_audio> [opsi]

Contoh:
    python transcribe.py rekaman_kuliah.m4a
    python transcribe.py rekaman.m4a --model medium --language id
    python transcribe.py rekaman.m4a --format txt srt --output D:\\Transkrip
"""

import argparse
import os
import sys
import time

# Fix encoding untuk Windows console (agar emoji dan karakter Unicode tampil)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from transcriber.utils import (
    validate_audio_file,
    check_ffmpeg,
    get_device_info,
    get_model_info,
    ensure_output_dir,
    format_duration,
    count_words,
    estimate_reading_time,
    print_banner,
)
from transcriber.core import transcribe_audio, AVAILABLE_MODELS
from transcriber.formatter import save_output


def create_parser() -> argparse.ArgumentParser:
    """Buat argument parser untuk CLI."""
    parser = argparse.ArgumentParser(
        prog="transcribe",
        description="🎙️ Audio Transcription Tool — Transkrip rekaman kuliah ke teks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python transcribe.py rekaman_kuliah.m4a
  python transcribe.py rekaman.m4a --model medium
  python transcribe.py rekaman.m4a --model small --language id
  python transcribe.py rekaman.m4a --format txt srt
  python transcribe.py rekaman.m4a --output D:\\Hasil_Transkrip

Model tersedia (kecil → besar):
  tiny      ~75 MB   | Tercepat, akurasi rendah
  base      ~145 MB  | Cepat, akurasi cukup
  small     ~470 MB  | Balance kecepatan & akurasi (default)
  medium    ~1.5 GB  | Akurasi tinggi
  large-v3  ~3 GB    | Paling akurat, paling lambat
        """,
    )

    parser.add_argument(
        "audio_file",
        type=str,
        nargs="?",
        default=None,
        help="Path ke file audio yang akan ditranskrip (mp3, wav, m4a, ogg, flac, dll)",
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default="small",
        choices=AVAILABLE_MODELS,
        help="Model Whisper yang digunakan (default: small)",
    )

    parser.add_argument(
        "--language", "-l",
        type=str,
        default=None,
        help="Kode bahasa, misal 'id' (Indonesia), 'en' (English). Default: auto-detect",
    )

    parser.add_argument(
        "--format", "-f",
        type=str,
        nargs="+",
        default=["txt"],
        choices=["txt", "srt"],
        help="Format output: txt, srt, atau keduanya (default: txt)",
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Direktori output. Default: folder 'output' di direktori ini",
    )

    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Tampilkan daftar model yang tersedia beserta detailnya",
    )

    return parser


def show_models():
    """Tampilkan daftar model Whisper yang tersedia."""
    models = get_model_info()
    device_info = get_device_info()

    print("\n📋 Model Whisper yang tersedia:\n")
    print(f"   {'Model':<12} {'Ukuran':<12} {'VRAM':<10} {'Deskripsi'}")
    print(f"   {'─' * 12} {'─' * 12} {'─' * 10} {'─' * 40}")

    for name, info in models.items():
        marker = " ★" if name == "small" else ""
        print(f"   {name:<12} {info['size']:<12} {info['vram']:<10} {info['description']}{marker}")

    print(f"\n   ★ = Recommended untuk hardware kamu")
    print(f"\n   🖥️  Device terdeteksi: {device_info['name']} ({device_info['type'].upper()})")
    if "vram_gb" in device_info:
        print(f"   💾 VRAM: {device_info['vram_gb']} GB")
    print()


def main():
    """Fungsi utama CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Tampilkan banner
    print_banner()

    # Jika hanya mau lihat daftar model
    if args.list_models:
        show_models()
        return

    # Cek apakah audio_file diberikan
    if args.audio_file is None:
        parser.print_help()
        print("\n❌ Error: File audio harus diberikan!")
        print("   Contoh: python transcribe.py rekaman_kuliah.m4a")
        sys.exit(1)

    # === STEP 1: Validasi prasyarat ===
    print("🔍 Memeriksa prasyarat...\n")

    # Cek FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg tidak ditemukan!")
        print("   FFmpeg diperlukan untuk memproses file audio.")
        print("")
        print("   Cara install (Windows):")
        print("   1. Buka PowerShell/Terminal")
        print("   2. Jalankan: winget install Gyan.FFmpeg")
        print("   3. Restart terminal")
        print("   4. Cek: ffmpeg -version")
        print("")
        sys.exit(1)
    print("   ✅ FFmpeg ditemukan")

    # Cek device
    device_info = get_device_info()
    if device_info["type"] == "cuda":
        print(f"   ✅ GPU ditemukan: {device_info['name']} ({device_info.get('vram_gb', '?')} GB VRAM)")
    else:
        print(f"   ℹ️  GPU CUDA tidak terdeteksi, menggunakan CPU")
    print()

    # === STEP 2: Validasi file audio ===
    try:
        audio_path = validate_audio_file(args.audio_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}")
        sys.exit(1)

    audio_filename = os.path.basename(audio_path)
    audio_basename = os.path.splitext(audio_filename)[0]
    print(f"🎵 File audio: {audio_filename}")
    print(f"   Path: {audio_path}")

    # === STEP 3: Setup output ===
    if args.output:
        output_dir = ensure_output_dir(args.output)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = ensure_output_dir(os.path.join(script_dir, "output"))

    print(f"📁 Output: {output_dir}")
    print(f"📝 Format: {', '.join(args.format)}")

    # === STEP 4: Transkripsi ===
    print("\n" + "─" * 50)
    print("  MULAI TRANSKRIPSI")
    print("─" * 50)

    try:
        result = transcribe_audio(
            file_path=audio_path,
            model_name=args.model,
            language=args.language,
        )
    except Exception as e:
        print(f"\n❌ Error saat transkripsi: {e}")
        sys.exit(1)

    # === STEP 5: Simpan output ===
    print("\n" + "─" * 50)
    print("  MENYIMPAN HASIL")
    print("─" * 50 + "\n")

    saved_files = save_output(result, output_dir, audio_basename, args.format)

    for f in saved_files:
        print(f"   💾 Disimpan: {f}")

    # === STEP 6: Ringkasan ===
    word_count = count_words(result["text"])
    reading_time = estimate_reading_time(word_count)

    print("\n" + "═" * 50)
    print("  ✅ TRANSKRIPSI BERHASIL!")
    print("═" * 50)
    print(f"   Durasi audio     : {format_duration(result['duration'])}")
    print(f"   Waktu proses     : {format_duration(result['processing_time'])}")
    print(f"   Jumlah kata      : {word_count:,} kata")
    print(f"   Estimasi baca    : ~{reading_time} menit")
    print(f"   Model            : {result['model']}")
    print(f"   Device           : {result['device'].upper()}")
    print("═" * 50)
    print()


if __name__ == "__main__":
    main()
