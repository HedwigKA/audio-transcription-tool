"""
Topic Analyzer module.
Menggunakan Google Gemini API untuk menganalisis dan mengelompokkan
transkrip berdasarkan topik bahasan secara otomatis.
"""

import json
import os
import sys

from .formatter import merge_to_paragraphs, format_duration


def get_api_key(api_key_arg: str = None) -> str:
    """
    Dapatkan Gemini API key dari berbagai sumber.
    
    Urutan prioritas:
    1. Argumen langsung (--api-key)
    2. Environment variable GEMINI_API_KEY
    3. File .env di folder project
    
    Args:
        api_key_arg: API key dari argumen CLI
        
    Returns:
        API key string
        
    Raises:
        ValueError: Jika API key tidak ditemukan
    """
    # 1. Dari argumen CLI
    if api_key_arg:
        return api_key_arg
    
    # 2. Dari environment variable
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
    
    # 3. Dari file .env
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return key
    
    raise ValueError(
        "Gemini API key tidak ditemukan!\n\n"
        "Cara mendapatkan API key (GRATIS):\n"
        "  1. Buka https://aistudio.google.com/apikey\n"
        "  2. Klik 'Create API Key'\n"
        "  3. Copy API key (dimulai dengan 'AIzaSy...')\n\n"
        "Cara menggunakan API key:\n"
        "  Opsi 1: python transcribe.py audio.m4a --topics --api-key AIzaSy...\n"
        "  Opsi 2: set GEMINI_API_KEY=AIzaSy...  (environment variable)\n"
        "  Opsi 3: Buat file .env dengan isi: GEMINI_API_KEY=AIzaSy..."
    )


def analyze_topics(paragraphs: list, api_key: str, language: str = "id") -> list:
    """
    Analisis transkrip dan kelompokkan berdasarkan topik menggunakan Gemini.
    
    Args:
        paragraphs: List paragraf (dari merge_to_paragraphs)
        api_key: Google Gemini API key
        language: Kode bahasa transkrip
        
    Returns:
        List topik, masing-masing berisi:
        - "title": Judul topik
        - "start": Waktu mulai (detik)
        - "end": Waktu akhir (detik)
        - "content": Teks isi topik (gabungan paragraf)
    """
    from google import genai
    
    # Siapkan teks transkrip dengan timestamp untuk konteks
    transcript_text = ""
    for para in paragraphs:
        start_ts = format_duration(para["start"])
        end_ts = format_duration(para["end"])
        transcript_text += f"[{start_ts} - {end_ts}]\n{para['text']}\n\n"
    
    # Prompt untuk Gemini
    lang_instruction = "Bahasa Indonesia" if language == "id" else "the same language as the transcript"
    
    prompt = f"""Kamu adalah asisten yang menganalisis transkrip rekaman kuliah/pertemuan.

Tugas: Analisis transkrip berikut dan kelompokkan berdasarkan TOPIK BAHASAN. Identifikasi kapan pembicara berpindah topik.

Aturan:
1. Beri judul singkat dan deskriptif untuk setiap topik (dalam {lang_instruction})
2. Kelompokkan paragraf yang membahas topik yang sama, meskipun pembicara kembali ke topik tersebut di waktu yang berbeda
3. Sertakan waktu mulai dan akhir setiap topik
4. Gabungkan teks paragraf yang relevan ke setiap topik
5. Urutkan topik berdasarkan waktu kemunculan pertamanya

PENTING: Respond HANYA dalam format JSON array berikut, tanpa markdown code block:
[
  {{
    "title": "Judul Topik",
    "start_time": "HH:MM:SS",
    "end_time": "HH:MM:SS",
    "paragraph_indices": [0, 1, 2]
  }}
]

paragraph_indices adalah indeks paragraf (dimulai dari 0) yang termasuk dalam topik tersebut.

TRANSKRIP:
{transcript_text}
"""

    print("\n🤖 Menganalisis topik dengan Gemini AI...")
    print("   Mohon tunggu, proses ini memakan waktu beberapa detik...\n")
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        
        response_text = response.text.strip()
        
        # Bersihkan response dari markdown code block jika ada
        if response_text.startswith("```"):
            # Hapus ```json dan ``` di akhir
            lines = response_text.split("\n")
            response_text = "\n".join(
                line for line in lines 
                if not line.strip().startswith("```")
            )
        
        topic_data = json.loads(response_text)
        
    except json.JSONDecodeError as e:
        print(f"⚠️  Gagal memproses response Gemini (format JSON tidak valid)")
        print(f"   Error: {e}")
        print(f"   Menggunakan fallback: seluruh transkrip sebagai 1 topik")
        return _fallback_single_topic(paragraphs)
    except Exception as e:
        print(f"⚠️  Error saat menghubungi Gemini API: {e}")
        print(f"   Menggunakan fallback: seluruh transkrip sebagai 1 topik")
        return _fallback_single_topic(paragraphs)
    
    # Bangun output topik
    topics = []
    for item in topic_data:
        indices = item.get("paragraph_indices", [])
        
        # Kumpulkan teks dari paragraf yang relevan
        topic_paragraphs = []
        topic_start = None
        topic_end = None
        
        for idx in indices:
            if 0 <= idx < len(paragraphs):
                para = paragraphs[idx]
                topic_paragraphs.append(para["text"])
                
                if topic_start is None or para["start"] < topic_start:
                    topic_start = para["start"]
                if topic_end is None or para["end"] > topic_end:
                    topic_end = para["end"]
        
        if topic_paragraphs:
            topics.append({
                "title": item.get("title", "Topik Tanpa Judul"),
                "start": topic_start,
                "end": topic_end,
                "content": "\n\n".join(topic_paragraphs),
            })
    
    if not topics:
        return _fallback_single_topic(paragraphs)
    
    print(f"   ✅ Terdeteksi {len(topics)} topik bahasan\n")
    for i, topic in enumerate(topics, 1):
        print(f"   📌 Topik {i}: {topic['title']}")
    print()
    
    return topics


def _fallback_single_topic(paragraphs: list) -> list:
    """Fallback: jadikan seluruh transkrip sebagai satu topik."""
    if not paragraphs:
        return []
    
    all_text = "\n\n".join(p["text"] for p in paragraphs)
    return [{
        "title": "Transkrip Lengkap",
        "start": paragraphs[0]["start"],
        "end": paragraphs[-1]["end"],
        "content": all_text,
    }]


def analyze_topics_from_result(result: dict, api_key: str,
                                gap_threshold: float = 1.5) -> list:
    """
    Wrapper: analisis topik langsung dari hasil transkripsi.
    
    Args:
        result: Dict hasil dari transcribe_audio()
        api_key: Google Gemini API key
        gap_threshold: Jeda untuk paragraph merging
        
    Returns:
        List topik
    """
    # Pertama, merge segmen ke paragraf
    paragraphs = merge_to_paragraphs(result["segments"], gap_threshold)
    
    # Lalu analisis topik
    language = result.get("language", "id")
    return analyze_topics(paragraphs, api_key, language)
