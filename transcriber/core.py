"""
Core transcription module.
Menangani loading model Whisper dan proses transkripsi audio.
"""

import sys
import time
import whisper

from .utils import check_cuda, get_device_info, format_duration


# Model yang tersedia
AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large-v3"]


def load_model(model_name: str = "small", device: str = None) -> whisper.Whisper:
    """
    Load model Whisper ke memory.
    
    Args:
        model_name: Nama model ("tiny", "base", "small", "medium", "large-v3")
        device: Device target ("cuda" atau "cpu"). None = auto-detect.
        
    Returns:
        Model Whisper yang sudah di-load
        
    Raises:
        ValueError: Jika nama model tidak valid
    """
    if model_name not in AVAILABLE_MODELS:
        available = ", ".join(AVAILABLE_MODELS)
        raise ValueError(
            f"Model '{model_name}' tidak valid.\n"
            f"Model tersedia: {available}"
        )
    
    # Auto-detect device
    if device is None:
        device = "cuda" if check_cuda() else "cpu"
    
    device_info = get_device_info()
    
    print(f"\n📦 Loading model '{model_name}'...")
    print(f"   Device: {device_info['name']} ({device_info['type'].upper()})")
    if "vram_gb" in device_info:
        print(f"   VRAM  : {device_info['vram_gb']} GB")
    
    start_time = time.time()
    
    try:
        model = whisper.load_model(model_name, device=device)
    except RuntimeError as e:
        # Jika GPU kehabisan VRAM, fallback ke CPU
        if "out of memory" in str(e).lower() or "CUDA" in str(e):
            print(f"\n⚠️  GPU VRAM tidak cukup untuk model '{model_name}'.")
            print(f"   Otomatis beralih ke CPU...")
            
            # Bersihkan GPU memory
            import torch
            torch.cuda.empty_cache()
            
            model = whisper.load_model(model_name, device="cpu")
            device = "cpu"
        else:
            raise
    
    load_time = time.time() - start_time
    print(f"   ✅ Model loaded dalam {load_time:.1f} detik\n")
    
    return model


def transcribe_audio(
    file_path: str,
    model_name: str = "small",
    language: str = None,
    device: str = None,
) -> dict:
    """
    Transkrip file audio menggunakan Whisper.
    
    Args:
        file_path: Path ke file audio
        model_name: Nama model Whisper
        language: Kode bahasa ("id", "en", dll). None = auto-detect.
        device: Device target. None = auto-detect.
        
    Returns:
        Dict berisi:
        - "text": Teks lengkap hasil transkripsi
        - "segments": List segmen dengan timestamp
        - "language": Bahasa yang terdeteksi
        - "duration": Durasi audio dalam detik
        - "model": Nama model yang digunakan
        - "device": Device yang digunakan
        - "processing_time": Waktu proses dalam detik
    """
    # Load model
    model = load_model(model_name, device)
    
    # Tentukan device aktual
    actual_device = next(model.parameters()).device.type
    
    # Opsi transkripsi
    transcribe_options = {
        "verbose": False,      # Kita handle progress sendiri
        "fp16": actual_device == "cuda",  # FP16 hanya di GPU
    }
    
    if language:
        transcribe_options["language"] = language
        print(f"🌐 Bahasa: {language}")
    else:
        print(f"🌐 Bahasa: auto-detect")
    
    print(f"🎵 Memproses audio: {file_path}")
    print(f"   Mohon tunggu, proses ini bisa memakan waktu...\n")
    
    # Progress indicator
    start_time = time.time()
    
    # Jalankan transkripsi
    result = whisper.transcribe(model, file_path, **transcribe_options)
    
    processing_time = time.time() - start_time
    
    # Hitung durasi audio dari segment terakhir
    audio_duration = 0
    if result["segments"]:
        audio_duration = result["segments"][-1]["end"]
    
    # Detected language
    detected_language = result.get("language", "unknown")
    
    print(f"\n✅ Transkripsi selesai!")
    print(f"   Durasi audio    : {format_duration(audio_duration)}")
    print(f"   Waktu proses    : {format_duration(processing_time)}")
    print(f"   Bahasa terdeteksi: {detected_language}")
    print(f"   Jumlah segmen   : {len(result['segments'])}")
    
    # Susun output
    output = {
        "text": result["text"].strip(),
        "segments": [
            {
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
            for seg in result["segments"]
        ],
        "language": detected_language,
        "duration": audio_duration,
        "model": model_name,
        "device": actual_device,
        "processing_time": processing_time,
    }
    
    return output
