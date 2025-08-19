# YouTube Video to Text Converter
# برنامه تبدیل ویدیو YouTube به متن

A Python program that downloads YouTube videos and converts speech to text with support for Persian/Farsi language.

برنامه‌ای که ویدیوهای YouTube را دانلود کرده و گفتار را به متن تبدیل می‌کند با پشتیبانی از زبان فارسی.

## Features / ویژگی‌ها

- ✅ Download audio from YouTube videos
- ✅ Convert speech to text using Google Speech Recognition
- ✅ Support for Persian/Farsi language (fa-IR)
- ✅ Automatic fallback to English if Persian fails
- ✅ Split long audio into manageable chunks
- ✅ Save output as both TXT and JSON files
- ✅ Clean up temporary files automatically

## Installation / نصب

### Prerequisites / پیش‌نیازها

1. **Python 3.7+** installed on your system
2. **FFmpeg** for audio processing

### Install FFmpeg / نصب FFmpeg

#### Windows:
1. Download FFmpeg from: https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

#### macOS:
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### Install Python Dependencies / نصب وابستگی‌های Python

```bash
pip install -r requirements.txt
```

## Usage / استفاده

### Basic Usage / استفاده پایه

```bash
python runtext.py
```

The program will:
1. Ask for a YouTube URL
2. Download the audio
3. Convert speech to text
4. Save results to `transcript.txt` and `transcript.json`

### Example / مثال

```
==================================================
برنامه تبدیل ویدیو YouTube به متن
YouTube Video to Text Converter
==================================================
لطفاً آدرس ویدیو YouTube را وارد کنید: https://www.youtube.com/watch?v=dQw4w9WgXcQ

شروع فرآیند تبدیل ویدیو به متن...
شناسه ویدیو: dQw4w9WgXcQ
در حال دانلود فایل صوتی...
دانلود فایل صوتی کامل شد!
در حال تقسیم فایل صوتی به قطعات...
فایل صوتی به 15 قطعه تقسیم شد
در حال تبدیل گفتار به متن...
پردازش قطعه 1/15...
...
✅ فرآیند با موفقیت کامل شد!
فایل‌های خروجی:
- transcript.txt: متن ساده
- transcript.json: اطلاعات کامل
```

## Output Files / فایل‌های خروجی

### transcript.txt
Plain text file containing the transcribed speech.

### transcript.json
Structured JSON file with:
- `video_id`: YouTube video ID
- `url`: Original YouTube URL
- `transcript`: Full transcribed text
- `chunks`: Array of individual audio chunk transcriptions

## Troubleshooting / عیب‌یابی

### Common Issues / مشکلات رایج

1. **FFmpeg not found**: Make sure FFmpeg is installed and in your PATH
2. **Audio download fails**: Check your internet connection and YouTube URL
3. **Speech recognition fails**: Ensure good audio quality and clear speech
4. **Persian text not recognized**: The program will automatically fallback to English

### Error Messages / پیام‌های خطا

- `خطا در دانلود`: Download error - check URL and internet connection
- `خطا: آدرس YouTube نامعتبر است`: Invalid YouTube URL
- `قطعه X: تشخیص داده نشد`: Speech not recognized in chunk X
- `خطا در اتصال`: Network connection error

## Requirements / نیازمندی‌ها

- Python 3.7+
- FFmpeg
- Internet connection
- YouTube video URL

## Dependencies / وابستگی‌ها

- `yt-dlp`: YouTube video downloader
- `SpeechRecognition`: Speech-to-text conversion
- `pydub`: Audio processing
- `PyAudio`: Audio I/O

## License / مجوز

This project is open source and available under the MIT License.

## Support / پشتیبانی

For issues and questions, please check the troubleshooting section above or create an issue in the repository.
