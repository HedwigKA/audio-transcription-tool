# 🎙️ Audio Transcription Tool

Convert audio recordings into readable text transcripts using **OpenAI Whisper** — completely free, offline, and supporting 90+ languages.

Turn hours of audio into text you can read in minutes. Perfect for lectures, meetings, interviews, podcasts, and more.

---

## ✨ Features

- 🎵 **Audio to text transcription** — supports `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm`, `.wma`, `.aac`
- ⏱️ **Timestamps per segment** — each paragraph is marked with time `[00:15:30]` for easy navigation
- 🤖 **Multiple model choices** — from `tiny` (fastest) to `large-v3` (most accurate)
- 📄 **Dual output formats** — `.txt` (clean text + timestamps) and `.srt` (subtitle format)
- 🌐 **Auto language detection** — supports multilingual & code-switching (e.g., mixing languages)
- ⚡ **GPU accelerated** — automatically uses NVIDIA GPU (CUDA) when available, falls back to CPU
- 📊 **Auto summary** — includes duration, word count, and estimated reading time in output

---

## 📋 Requirements

- **Python** 3.8 or higher
- **FFmpeg** (required for audio processing)
- **NVIDIA GPU** (optional, for faster processing via CUDA)

---

## 🔧 Installation

### 1. Install Python

Make sure Python 3.8+ is installed:

```bash
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/).

<details>
<summary>Windows (via winget)</summary>

```powershell
winget install Python.Python.3.12
```

> ⚠️ During installation, check ✅ **"Add Python to PATH"**

</details>

### 2. Install FFmpeg

FFmpeg is required by Whisper to read audio files.

<details>
<summary>Windows</summary>

```powershell
winget install Gyan.FFmpeg
```

After installation, **restart your terminal**, then verify:

```powershell
ffmpeg -version
```

</details>

<details>
<summary>macOS</summary>

```bash
brew install ffmpeg
```

</details>

<details>
<summary>Linux (Ubuntu/Debian)</summary>

```bash
sudo apt update && sudo apt install ffmpeg
```

</details>

### 3. Clone & Install Dependencies

```bash
git clone https://github.com/HedwigKA/audio-transcription-tool.git
cd audio-transcription-tool
pip install -r requirements.txt
```

### 4. (Optional) Enable GPU Acceleration

If you have an NVIDIA GPU, install PyTorch with CUDA for significantly faster transcription:

```bash
pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu126
```

> 💡 Check if your GPU is detected:
> ```bash
> python transcribe.py --list-models
> ```

### 5. Verify Installation

```bash
python transcribe.py --list-models
```

If successful, you'll see a list of available Whisper models and your device info.

---

## 🚀 Usage

### Basic Usage

```bash
python transcribe.py your_audio_file.m4a
```

This will:
1. Use the `small` model (default — good balance of speed & accuracy)
2. Auto-detect the language
3. Save the transcript to the `output/` folder as a `.txt` file

### Choose a Model

```bash
# Fastest, lower accuracy (good for quick tests)
python transcribe.py audio.m4a --model tiny

# Balanced speed & accuracy (default, recommended)
python transcribe.py audio.m4a --model small

# High accuracy
python transcribe.py audio.m4a --model medium

# Highest accuracy (slowest, may run on CPU if GPU VRAM < 10 GB)
python transcribe.py audio.m4a --model large-v3
```

### Specify Language

```bash
# Force Indonesian
python transcribe.py audio.m4a --language id

# Force English
python transcribe.py audio.m4a --language en

# Auto-detect (default, recommended for multilingual audio)
python transcribe.py audio.m4a
```

> 💡 Whisper supports 90+ languages. See the full list [here](https://github.com/openai/whisper#available-models-and-languages).

### Choose Output Format

```bash
# Text only (default)
python transcribe.py audio.m4a --format txt

# Subtitle only
python transcribe.py audio.m4a --format srt

# Both
python transcribe.py audio.m4a --format txt srt
```

### Custom Output Directory

```bash
python transcribe.py audio.m4a --output /path/to/output
```

### Full Example

```bash
python transcribe.py "Meeting Recording.m4a" --model medium --language en --format txt srt --output ./transcripts
```

### Short Flags

```bash
python transcribe.py audio.m4a -m medium -l en -f txt srt -o ./transcripts
```

---

## 📊 Model Comparison

| Model | Size | VRAM | Speed (2h audio) | Accuracy | Notes |
|---|---|---|---|---|---|
| `tiny` | ~75 MB | ~1 GB | ~5-10 min | ⭐⭐ | Best for quick tests |
| `base` | ~145 MB | ~1 GB | ~10-15 min | ⭐⭐⭐ | Good for clear audio |
| `small` | ~470 MB | ~2 GB | ~15-30 min | ⭐⭐⭐⭐ | **Recommended** for most users |
| `medium` | ~1.5 GB | ~5 GB | ~30-60 min | ⭐⭐⭐⭐⭐ | Great accuracy, needs more VRAM |
| `large-v3` | ~3 GB | ~10 GB | ~2-4 hrs | ⭐⭐⭐⭐⭐+ | Best accuracy, needs powerful GPU |

> ⏱️ Speed estimates assume GPU acceleration. CPU-only processing will be significantly slower.

---

## 📂 Output Examples

### `.txt` Output

```
════════════════════════════════════════════════════════════
  TRANSKRIP AUDIO
  Durasi Audio  : 01:58:23
  Jumlah Kata   : 12,450 kata
  Estimasi Baca : ~25 menit
  Model         : small
  Bahasa        : English (auto-detected)
  Device        : CUDA
  Waktu Proses  : 00:22:15
════════════════════════════════════════════════════════════

[00:00:15] Welcome everyone. Today we're going to discuss
the fundamentals of machine learning.

[00:02:30] Machine learning is essentially a branch of
artificial intelligence that focuses on...

[00:05:12] So the key concept here is supervised learning,
where we have labeled training data...
```

### `.srt` Output

```
1
00:00:15,000 --> 00:00:45,200
Welcome everyone. Today we're going to discuss
the fundamentals of machine learning.

2
00:02:30,000 --> 00:03:10,500
Machine learning is essentially a branch of
artificial intelligence that focuses on...
```

> 💡 `.srt` files can be used as subtitles in media players like VLC, PotPlayer, or MPV!

---

## ❓ Troubleshooting

### FFmpeg not found

```
❌ FFmpeg tidak ditemukan!
```

**Solution:** Install FFmpeg (see [Installation](#2-install-ffmpeg)) and restart your terminal.

### CUDA not available (with NVIDIA GPU)

**Solution:**
1. Update your NVIDIA drivers: [nvidia.com/drivers](https://www.nvidia.com/drivers)
2. Reinstall PyTorch with CUDA:
   ```bash
   pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu126
   ```

### Out of memory during transcription

**Solution:** Use a smaller model: `--model small` or `--model base`. The tool will also automatically fall back to CPU if GPU runs out of VRAM.

### Inaccurate transcription results

**Solution:**
1. Use a larger model: `--model medium` or `--model large-v3`
2. Specify the language: `--language en` (if mostly English)
3. Ensure the audio quality is clear with minimal background noise

### Processing takes too long

**Solution:**
- Use a smaller model: `--model tiny` or `--model base`
- Make sure GPU CUDA is detected: `python transcribe.py --list-models`

---

## 📁 Project Structure

```
audio-transcription-tool/
├── transcribe.py          # CLI entry point (run this)
├── transcriber/
│   ├── __init__.py        # Package init
│   ├── core.py            # Whisper transcription logic
│   ├── formatter.py       # Output formatting (TXT, SRT)
│   └── utils.py           # Helper functions
├── output/                # Transcription results saved here
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md              # This file
```

---

## 🛠️ Built With

- **[OpenAI Whisper](https://github.com/openai/whisper)** — Open-source speech-to-text model
- **[PyTorch](https://pytorch.org/)** — Deep learning framework (Whisper backend)
- **[FFmpeg](https://ffmpeg.org/)** — Audio/video processing
- **Python 3.8+**

---

## 📄 License

This project is for personal and educational use. OpenAI Whisper is licensed under the [MIT License](https://github.com/openai/whisper/blob/main/LICENSE).
