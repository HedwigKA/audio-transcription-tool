# 🎙️ Audio Transcription Tool

Transkrip rekaman audio kuliah menjadi teks menggunakan **OpenAI Whisper**.

Dengan tool ini, kamu bisa mengubah rekaman kuliah 2 jam menjadi teks yang bisa dibaca dalam ~25 menit — jauh lebih efisien daripada mendengarkan ulang seluruh rekaman!

---

## 📋 Fitur

- ✅ **Transkripsi audio ke teks** — mendukung `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm`, `.wma`, `.aac`
- ✅ **Timestamp per segmen** — setiap paragraf ditandai waktu `[00:15:30]`
- ✅ **Pilih model** — dari `tiny` (tercepat) sampai `large-v3` (paling akurat)
- ✅ **Multi-format output** — `.txt` (teks + timestamp) dan `.srt` (subtitle)
- ✅ **Auto-detect bahasa** — mendukung bilingual (Indonesia + English)
- ✅ **GPU accelerated** — otomatis menggunakan NVIDIA GPU jika tersedia
- ✅ **Ringkasan otomatis** — info durasi, jumlah kata, dan estimasi waktu baca

---

## 🔧 Instalasi

### 1. Install Python

Pastikan Python 3.8+ sudah terinstall. Cek dengan:

```powershell
python --version
```

Jika belum, download di [python.org](https://www.python.org/downloads/) atau install via:

```powershell
winget install Python.Python.3.12
```

> ⚠️ **Penting:** Saat install Python, centang ✅ **"Add Python to PATH"**

### 2. Install FFmpeg

FFmpeg diperlukan oleh Whisper untuk membaca file audio.

```powershell
winget install Gyan.FFmpeg
```

Setelah install, **tutup dan buka ulang terminal**, lalu verifikasi:

```powershell
ffmpeg -version
```

Jika berhasil, akan muncul informasi versi FFmpeg.

<details>
<summary>❓ Alternatif instalasi FFmpeg</summary>

**Via Chocolatey:**
```powershell
choco install ffmpeg
```

**Manual:**
1. Download dari [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Pilih "Windows builds from gyan.dev"
3. Download versi `ffmpeg-release-essentials.zip`
4. Extract ke folder, misal `C:\ffmpeg`
5. Tambahkan `C:\ffmpeg\bin` ke System PATH:
   - Buka Settings → System → About → Advanced System Settings
   - Environment Variables → Path → Edit → New
   - Tambahkan `C:\ffmpeg\bin`
   - OK → OK → Restart terminal

</details>

### 3. Install Dependencies Python

Buka terminal di folder project ini, lalu jalankan:

```powershell
cd "D:\Transkrip Python"
pip install -r requirements.txt
```

> ℹ️ Proses ini akan menginstall **OpenAI Whisper** beserta **PyTorch** (dengan CUDA support jika GPU NVIDIA terdeteksi). Ukuran download bisa mencapai ~2 GB untuk pertama kali.

### 4. Verifikasi Instalasi

```powershell
python transcribe.py --list-models
```

Jika berhasil, akan tampil daftar model Whisper dan informasi GPU kamu.

---

## 🚀 Cara Penggunaan

### Penggunaan Dasar

```powershell
python transcribe.py rekaman_kuliah.m4a
```

Ini akan:
1. Menggunakan model `small` (default, cocok untuk RTX 3050)
2. Auto-detect bahasa (mendukung campuran Indonesia + English)
3. Menyimpan hasil di folder `output/` sebagai file `.txt`

### Pilih Model

```powershell
# Model kecil & cepat (untuk tes atau audio pendek)
python transcribe.py rekaman.m4a --model tiny

# Model balance (default, recommended)
python transcribe.py rekaman.m4a --model small

# Model presisi tinggi
python transcribe.py rekaman.m4a --model medium

# Model paling akurat (lambat, jalan di CPU jika VRAM < 10 GB)
python transcribe.py rekaman.m4a --model large-v3
```

### Tentukan Bahasa

```powershell
# Paksa bahasa Indonesia
python transcribe.py rekaman.m4a --language id

# Paksa bahasa Inggris
python transcribe.py rekaman.m4a --language en

# Auto-detect (default, recommended untuk dosen bilingual)
python transcribe.py rekaman.m4a
```

### Pilih Format Output

```powershell
# Hanya TXT (default)
python transcribe.py rekaman.m4a --format txt

# Hanya SRT (subtitle)
python transcribe.py rekaman.m4a --format srt

# Keduanya
python transcribe.py rekaman.m4a --format txt srt
```

### Tentukan Folder Output

```powershell
python transcribe.py rekaman.m4a --output D:\Hasil_Transkrip
```

### Kombinasi Lengkap

```powershell
python transcribe.py "D:\Rekaman\Kuliah ML Week 3.m4a" --model medium --language id --format txt srt --output D:\Transkrip
```

### Shortcut (Flag Pendek)

```powershell
python transcribe.py rekaman.m4a -m medium -l id -f txt srt -o D:\Transkrip
```

---

## 📊 Perbandingan Model

| Model | Ukuran | VRAM | Estimasi Waktu (audio 2 jam) | Akurasi | RTX 3050 (4GB) |
|---|---|---|---|---|---|
| `tiny` | ~75 MB | ~1 GB | ~5-10 menit | ⭐⭐ | ✅ Lancar |
| `base` | ~145 MB | ~1 GB | ~10-15 menit | ⭐⭐⭐ | ✅ Lancar |
| `small` | ~470 MB | ~2 GB | ~15-30 menit | ⭐⭐⭐⭐ | ✅ Lancar (**Recommended**) |
| `medium` | ~1.5 GB | ~5 GB | ~30-60 menit | ⭐⭐⭐⭐⭐ | ⚠️ Mepet, mungkin fallback CPU |
| `large-v3` | ~3 GB | ~10 GB | ~2-4 jam | ⭐⭐⭐⭐⭐+ | ❌ Jalan di CPU |

> 💡 **Tip:** Untuk penggunaan sehari-hari, gunakan `small`. Untuk rekaman ujian/penting, coba `medium`.

---

## 📂 Contoh Hasil Output

### File `.txt`

```
════════════════════════════════════════════════════════════
  TRANSKRIP AUDIO
  Durasi Audio  : 01:58:23
  Jumlah Kata   : 12,450 kata
  Estimasi Baca : ~25 menit
  Model         : small
  Bahasa        : Indonesian (auto-detected)
  Device        : CUDA
  Waktu Proses  : 00:22:15
════════════════════════════════════════════════════════════

[00:00:15] Baik, selamat pagi semuanya. Hari ini kita akan
membahas tentang konsep dasar machine learning.

[00:02:30] Machine learning itu pada dasarnya adalah cabang
dari artificial intelligence yang fokus pada...

[00:05:12] So the key concept here is supervised learning,
where we have labeled training data...

[00:05:45] Nah, kalau di Python kita bisa pakai library
scikit-learn untuk implementasinya.
```

### File `.srt`

```
1
00:00:15,000 --> 00:00:45,200
Baik, selamat pagi semuanya. Hari ini kita akan membahas
tentang konsep dasar machine learning.

2
00:02:30,000 --> 00:03:10,500
Machine learning itu pada dasarnya adalah cabang dari
artificial intelligence yang fokus pada...
```

> 💡 **Tip:** File `.srt` bisa langsung digunakan sebagai subtitle di video player seperti VLC!

---

## ❓ Troubleshooting

### "FFmpeg not found"

```
❌ FFmpeg tidak ditemukan!
```

**Solusi:**
1. Install FFmpeg: `winget install Gyan.FFmpeg`
2. Tutup dan buka ulang terminal
3. Cek: `ffmpeg -version`

### "CUDA not available" (padahal punya GPU NVIDIA)

**Solusi:**
1. Pastikan driver NVIDIA terbaru: [nvidia.com/drivers](https://www.nvidia.com/drivers)
2. Reinstall PyTorch dengan CUDA:
   ```powershell
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### "Out of memory" saat transkripsi

**Solusi:**
- Gunakan model yang lebih kecil: `--model small` atau `--model base`
- Tool akan otomatis fallback ke CPU jika GPU kehabisan VRAM

### Hasil transkripsi kurang akurat

**Solusi:**
1. Gunakan model lebih besar: `--model medium` atau `--model large-v3`
2. Tentukan bahasa: `--language id` (jika mayoritas Indonesia)
3. Pastikan kualitas audio cukup jelas (minim noise)

### Proses terlalu lama

**Solusi:**
- Gunakan model lebih kecil: `--model tiny` atau `--model base`
- Pastikan GPU CUDA terdeteksi (cek dengan `python transcribe.py --list-models`)

---

## 📁 Struktur Project

```
Transkrip Python/
├── transcribe.py          # CLI entry point (jalankan ini)
├── transcriber/
│   ├── __init__.py        # Package init
│   ├── core.py            # Logic transkripsi Whisper
│   ├── formatter.py       # Format output (TXT, SRT)
│   └── utils.py           # Helper functions
├── output/                # Hasil transkrip disimpan di sini
├── requirements.txt       # Python dependencies
└── README.md              # File ini
```

---

## 🛠️ Teknologi

- **[OpenAI Whisper](https://github.com/openai/whisper)** — Model speech-to-text open-source
- **[PyTorch](https://pytorch.org/)** — Framework deep learning (backend Whisper)
- **[FFmpeg](https://ffmpeg.org/)** — Audio/video processing
- **Python 3.8+**

---

## 📄 Lisensi

Tool ini dibuat untuk keperluan pribadi/belajar. OpenAI Whisper dilisensikan di bawah MIT License.
