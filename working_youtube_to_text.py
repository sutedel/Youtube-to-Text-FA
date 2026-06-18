import os
import sys
import re
import time
from urllib.parse import urlparse, parse_qs
import speech_recognition as sr
import yt_dlp
import tempfile
import json
from persian_text_normalizer import normalize_text, segment_sentences, PersianTextNormalizer
from persian_domain_corrector import correct_text, WHISPER_INITIAL_PROMPT, WHISPER_HOTWORDS
from pydub import AudioSegment

class WorkingYouTubeToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

        # --- Speech-to-text engine configuration ---------------------------------
        # Primary engine is faster-whisper (much better for accented/colloquial
        # Persian). It falls back to Google Web Speech automatically if the package
        # or model can't be loaded. Override via environment variables if needed.
        self.whisper_model_size = os.getenv("WHISPER_MODEL", "large-v3")
        self.whisper_device = os.getenv("WHISPER_DEVICE", "auto")  # "cpu" | "cuda" | "auto"
        # int8 on CPU keeps memory/time reasonable; float16 is faster on GPU.
        self.whisper_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "")
        self._use_whisper = os.getenv("USE_WHISPER", "1") != "0"
        self._whisper_model = None  # lazy-loaded on first use
        
    def extract_video_id(self, url):
        """Extract YouTube video ID from URL"""
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        return None
    
    def download_audio(self, url, output_path="audio", max_minutes: int | None = None):
        """Download audio from YouTube video. If max_minutes is provided, only download that initial segment."""
        start_time = time.time()
        print("در حال دانلود فایل صوتی...")

        # Use absolute path inside output dir to avoid Windows fragment path issues
        abs_output_path = os.path.join(os.path.abspath(self.output_dir), "audio_download")
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best',
            'outtmpl': abs_output_path,
            'quiet': True,
            'no_warnings': True,
            'nopart': True,
        }

        # Limit download duration for quick tests
        if isinstance(max_minutes, int) and max_minutes > 0:
            # yt-dlp supports section downloads
            end_time = max_minutes * 60
            ydl_opts['download_sections'] = {'*': [{'start_time': 0, 'end_time': end_time}]}
            ydl_opts['force_keyframes_at_cuts'] = True
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                title = info.get('title') or "output"
                download_time = time.time() - start_time
                print(f"دانلود فایل صوتی کامل شد! (زمان: {download_time:.1f} ثانیه)")
                return downloaded_file, title, download_time
        except Exception as e:
            print(f"خطا در دانلود: {e}")
            return None
    
    def _resolve_compute_type(self, device: str) -> str:
        """Pick a sensible compute type when the user hasn't forced one."""
        if self.whisper_compute_type:
            return self.whisper_compute_type
        return "float16" if device == "cuda" else "int8"

    def _load_whisper(self):
        """Lazy-load the faster-whisper model. Returns the model or None if
        unavailable (caller then falls back to Google)."""
        if not self._use_whisper:
            return None
        if self._whisper_model is not None:
            return self._whisper_model
        try:
            from faster_whisper import WhisperModel
            device = self.whisper_device
            if device == "auto":
                # Detect an NVIDIA GPU through CTranslate2 itself (no torch needed).
                try:
                    import ctranslate2
                    device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
                except Exception:
                    device = "cpu"
                if device == "cpu":
                    print(
                        "ℹ️  GPU یافت نشد؛ Whisper روی CPU اجرا می‌شود (برای ویدیوهای بلند کند است). "
                        "برای سرعت بالا روی سیستم دارای GPU انویدیا اجرا کنید یا WHISPER_MODEL را کوچک‌تر کنید."
                    )
            compute_type = self._resolve_compute_type(device)
            print(
                f"در حال بارگذاری مدل Whisper ({self.whisper_model_size}) "
                f"روی {device} / {compute_type}..."
            )
            self._whisper_model = WhisperModel(
                self.whisper_model_size,
                device=device,
                compute_type=compute_type,
            )
            print("✅ مدل Whisper بارگذاری شد")
        except Exception as e:
            print(f"⚠️  بارگذاری Whisper ناموفق بود ({e}). به Google برمی‌گردیم.")
            self._use_whisper = False
            self._whisper_model = None
        return self._whisper_model

    def transcribe_audio_file(self, audio_path):
        """Transcribe an audio file. Uses faster-whisper when available (best
        quality for accented Persian), otherwise falls back to Google."""
        model = self._load_whisper()
        if model is not None:
            result = self._transcribe_with_whisper(model, audio_path)
            if result is not None:
                return result
        return self._transcribe_with_google(audio_path)

    def _transcribe_with_whisper(self, model, audio_path):
        """Transcribe with faster-whisper. Whisper handles long audio and its own
        VAD segmentation, and `initial_prompt` primes the domain vocabulary so
        accented terms (تیرکس، کندل، اف تی سی ...) are spelled correctly.
        Returns (text, seconds) or None to trigger the Google fallback."""
        start_time = time.time()
        print("در حال تبدیل گفتار به متن با Whisper...")
        try:
            segments, _info = model.transcribe(
                audio_path,
                language="fa",
                task="transcribe",
                initial_prompt=WHISPER_INITIAL_PROMPT,
                hotwords=WHISPER_HOTWORDS,
                beam_size=5,
                temperature=0.0,
                # False so hotwords bias EVERY window (not just the first) and to
                # avoid error/repetition propagation on long Persian lectures.
                condition_on_previous_text=False,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            parts = []
            for seg in segments:
                t = (seg.text or "").strip()
                if t:
                    parts.append(t)
            full_text = " ".join(parts).strip()
            transcription_time = time.time() - start_time
            print(
                f"تبدیل گفتار به متن کامل شد! (Whisper، زمان: {transcription_time:.1f} ثانیه)"
            )
            if not full_text:
                return "[گفتار تشخیص داده نشد - Speech not recognized]", transcription_time
            return full_text, transcription_time
        except Exception as e:
            print(f"❌ خطا در Whisper ({e}). تلاش با Google...")
            return None

    def _transcribe_with_google(self, audio_path):
        """Transcribe with Google Web Speech in ~55s chunks (fallback engine)."""
        start_time = time.time()
        print("در حال تبدیل گفتار به متن (Google)...")

        try:
            # Load and clean audio (mono, 16 kHz, high-pass + loudness normalize)
            segment = AudioSegment.from_file(audio_path)
            segment = segment.set_channels(1).set_frame_rate(16000)
            try:
                from pydub.effects import normalize as _normalize
                segment = segment.high_pass_filter(80)  # drop low-frequency rumble
                segment = _normalize(segment)           # even out loudness
            except Exception as _e:
                print(f"⚠️  بهبود صدا انجام نشد: {_e}")

            chunk_ms = 55_000  # slightly under 60s to reduce number of requests
            texts = []
            total_chunks = max(1, (len(segment) + chunk_ms - 1) // chunk_ms)

            did_adjust = False
            for idx in range(0, len(segment), chunk_ms):
                part = segment[idx: idx + chunk_ms]

                # Export temporary WAV for SpeechRecognition
                tmp_wav = None
                try:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
                        tmp_wav = tf.name
                    part.export(tmp_wav, format='wav')

                    with sr.AudioFile(tmp_wav) as source:
                        # Calibrate ambient noise once on a short window
                        if not did_adjust:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            did_adjust = True
                        audio_data = self.recognizer.record(source)

                    # Try Persian first, then English
                    try:
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language='fa-IR'
                        )
                        print("✅ متن فارسی تشخیص داده شد!")
                    except sr.UnknownValueError:
                        try:
                            text = self.recognizer.recognize_google(
                                audio_data,
                                language='en-US'
                            )
                            print("✅ متن انگلیسی تشخیص داده شد!")
                        except sr.UnknownValueError:
                            text = ""
                            print("❌ گفتار تشخیص داده نشد (بخشی از فایل)")
                    texts.append(text)
                finally:
                    if tmp_wav and os.path.exists(tmp_wav):
                        try:
                            os.remove(tmp_wav)
                        except:
                            pass

            transcription_time = time.time() - start_time
            print(f"تبدیل گفتار به متن کامل شد! (زمان: {transcription_time:.1f} ثانیه)")
            # Join chunks simply; sentence segmentation will handle readability
            full_text = " ".join(t for t in texts if t).strip()
            if not full_text:
                return "[گفتار تشخیص داده نشد - Speech not recognized]", transcription_time
            return full_text, transcription_time

        except sr.RequestError as e:
            print(f"❌ خطا در اتصال: {e}")
            return f"[خطا در اتصال به سرویس تشخیص گفتار - {e}]", 0
        except Exception as e:
            print(f"خطا در پردازش فایل صوتی: {e}")
            return f"[خطا در پردازش فایل صوتی - {e}]", 0
    
    def transcribe_video(self, url, output_file=None, max_minutes: int | None = None):
        """Main function to transcribe YouTube video"""
        total_start_time = time.time()
        print("شروع فرآیند تبدیل ویدیو به متن...")
        
        # Extract video ID and validate URL
        video_id = self.extract_video_id(url)
        if not video_id:
            print("خطا: آدرس YouTube نامعتبر است")
            return False
        
        print(f"شناسه ویدیو: {video_id}")
        
        # Download audio
        audio_result = self.download_audio(url, max_minutes=max_minutes)
        if not audio_result:
            return False
        audio_path, video_title, download_time = audio_result

        # Ensure we have a WAV file for SpeechRecognition
        wav_audio_path = self._ensure_wav(audio_path)

        # Reliably trim to the first max_minutes (the yt-dlp section download is
        # not honored for audio-only formats, so we cut the WAV ourselves).
        if isinstance(max_minutes, int) and max_minutes > 0:
            wav_audio_path = self._trim_wav(wav_audio_path, max_minutes)

        # Build output file base name from video title (max 20 chars)
        base_name = self._make_safe_basename(video_title, fallback=video_id, max_length=20)
        if not output_file:
            output_file = os.path.join(self.output_dir, f"{base_name}.txt")
        
        # Transcribe audio
        transcript_result = self.transcribe_audio_file(wav_audio_path)
        if isinstance(transcript_result, tuple):
            transcript_text, transcription_time = transcript_result
        else:
            transcript_text = transcript_result
            transcription_time = 0
        # Determine if meaningful text was produced (avoid deleting audio if not)
        text_produced = isinstance(transcript_text, str) and not transcript_text.strip().startswith('[')

        # Fix domain jargon mis-heard from accent/colloquial speech BEFORE
        # normalization (e.g. تیکس→تیرکس، ftc→اف تی سی، ASCII→Persian digits).
        if text_produced:
            transcript_text = correct_text(transcript_text)

        normalized_text = normalize_text(transcript_text)
        sentences = segment_sentences(normalized_text)

        # Re-apply domain corrections AFTER normalization so the (basic) normalizer
        # can't undo them (e.g. mapping «ئ»→«ی»). correct_text is idempotent.
        if text_produced:
            normalized_text = correct_text(normalized_text)
            sentences = [correct_text(s) for s in sentences]

        # Remove commas per user preference (both Persian and Latin)
        clean_normalized_text = normalized_text.replace('،', '').replace(',', '')
        clean_sentences = [s.replace('،', '').replace(',', '') for s in sentences]
        
        # Save transcript to file
        try:
            # Write sentences to .txt (one per line); fallback to normalized text if empty
            text_to_write = "\n".join(clean_sentences) if clean_sentences else clean_normalized_text
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_to_write)
            print(f"متن در فایل {output_file} ذخیره شد")
            
            # Also save as JSON for better structure
            json_output = {
                'video_id': video_id,
                'url': url,
                'title': video_title,
                'transcript': clean_normalized_text,
                'method': 'Google Speech Recognition',
                'sentences': clean_sentences
            }
            
            json_file = os.path.join(self.output_dir, f"{base_name}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            print(f"اطلاعات کامل در فایل {json_file} ذخیره شد")
            
            total_time = time.time() - total_start_time
            result_payload = {
                'text_file': output_file,
                'json_file': json_file,
                'title': video_title,
                'video_id': video_id,
                'timing': {
                    'download': download_time,
                    'transcription': transcription_time,
                    'total': total_time
                }
            }
            # Mark for deletion only if text was actually produced
            should_delete_audio = True if text_produced else False
            return result_payload
            
        except Exception as e:
            print(f"خطا در ذخیره فایل: {e}")
            return False
        
        finally:
            # Clean up audio files only if meaningful text was produced
            try:
                should_delete = locals().get('should_delete_audio', False)
                if should_delete:
                    if os.path.exists(audio_path):
                        try:
                            os.remove(audio_path)
                        except:
                            pass
                    if os.path.exists(wav_audio_path) and wav_audio_path != audio_path:
                        try:
                            os.remove(wav_audio_path)
                        except:
                            pass
                else:
                    print("ℹ️ فایل‌های صوتی برای بررسی نگه داشته شدند (عدم تولید متن).")
            except Exception:
                pass

    def _make_safe_basename(self, title, fallback, max_length=20):
        """Create a filesystem-safe basename from title, limited to max_length.
        Falls back to provided fallback (e.g., video_id) if result is empty.
        """
        if not isinstance(title, str):
            title = str(title or "")
        # Remove illegal Windows filename chars and normalize whitespace
        # Illegal: < > : " / \ | ? *
        title = re.sub(r'[<>:"/\\|?*]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        # Replace spaces with underscore for portability
        safe = title.replace(' ', '_')
        # Avoid trailing dots or spaces (Windows restriction)
        safe = safe.rstrip(' .')
        # Truncate to max_length
        if len(safe) > max_length:
            safe = safe[:max_length].rstrip('_')
        if not safe:
            safe = (fallback or "output")
        # Final cleanup and ensure not empty
        safe = re.sub(r'\s+', '_', safe).strip('_') or "output"
        return safe

    def _trim_wav(self, wav_path: str, max_minutes: int) -> str:
        """Write a trimmed copy containing only the first max_minutes. Returns the
        trimmed path, or the original path if trimming fails."""
        try:
            audio = AudioSegment.from_file(wav_path)
            limit_ms = max_minutes * 60 * 1000
            if len(audio) <= limit_ms:
                return wav_path
            trimmed = audio[:limit_ms]
            out_path = os.path.splitext(wav_path)[0] + f"_first{max_minutes}m.wav"
            trimmed.export(out_path, format="wav")
            print(f"✂️  صدا به {max_minutes} دقیقه‌ی اول بریده شد (برای تست).")
            return out_path
        except Exception as e:
            print(f"⚠️  بریدن صدا ناموفق بود: {e}")
            return wav_path

    def _ensure_wav(self, input_path: str) -> str:
        """Convert downloaded audio to WAV if needed. Returns path to WAV file.
        Requires FFmpeg available in PATH for pydub to work.
        """
        try:
            if input_path.lower().endswith('.wav'):
                return input_path
            output_path = os.path.splitext(input_path)[0] + '.wav'
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format='wav')
            return output_path
        except Exception as e:
            print(f"❌ تبدیل فایل صوتی به WAV ناموفق بود: {e}")
            print("برای رفع مشکل، FFmpeg را نصب کنید و دوباره تلاش کنید.")
            return input_path

def main():
    print("=" * 50)
    print("برنامه تبدیل ویدیو YouTube به متن (کارآمد)")
    print("Working YouTube Video to Text Converter")
    print("=" * 50)
    print()
    print("📝 این برنامه:")
    print("1. فایل صوتی ویدیو YouTube را دانلود می‌کند")
    print("2. گفتار را به متن تبدیل می‌کند")
    print("3. از زبان فارسی پشتیبانی می‌کند")
    print("4. در صورت عدم تشخیص فارسی، انگلیسی را امتحان می‌کند")
    print("5. برای تبدیل فرمت صوتی از FFmpeg استفاده می‌کند (به صورت خودکار)")
    print()
    print("⚠️  محدودیت‌ها:")
    print("- فقط فرمت‌های صوتی پشتیبانی شده کار می‌کنند")
    print("- کیفیت تشخیص به کیفیت صدا بستگی دارد")
    print("- نیاز به اتصال اینترنت برای تشخیص گفتار دارد")
    print()
    
    # Start timer when URL is entered
    overall_start_time = time.time()
    
    # Get YouTube URL from args or prompt, with optional --max-minutes
    max_minutes: int | None = None
    args = sys.argv[1:]
    url = None
    # Very light parsing to avoid bringing in argparse overhead
    if args:
        # Support: working_youtube_to_text.py --max-minutes 5 <url>
        if args[0] == '--max-minutes' and len(args) >= 3:
            try:
                max_minutes = int(args[1])
            except ValueError:
                max_minutes = None
            url = args[2].strip()
        else:
            url = args[0].strip()
        print(f"آدرس از خط فرمان دریافت شد: {url}")
        if max_minutes:
            print(f"فقط {max_minutes} دقیقه اول ویدیو پردازش خواهد شد (برای تست سریع)")
    if not url:
        url = input("لطفاً آدرس ویدیو YouTube را وارد کنید: ").strip()
    
    if not url:
        print("خطا: آدرس ویدیو وارد نشده است")
        return
    
    # Create converter instance
    converter = WorkingYouTubeToText()
    
    # Transcribe video
    result = converter.transcribe_video(url, max_minutes=max_minutes)
    
    # Calculate total time from URL entry to file generation
    total_overall_time = time.time() - overall_start_time
    
    if result:
        print("\n✅ فرآیند با موفقیت کامل شد!")
        print(f"\n⏱️  کل زمان از ورود لینک تا تولید فایل: {total_overall_time:.1f} ثانیه")
        print("\n📊 زمان‌بندی جزئی:")
        if isinstance(result, dict) and 'timing' in result:
            timing = result['timing']
            print(f"  📥 دانلود: {timing['download']:.1f} ثانیه")
            print(f"  🎤 تبدیل گفتار: {timing['transcription']:.1f} ثانیه")
            print(f"  ⚙️  پردازش داخلی: {timing['total'] - timing['download'] - timing['transcription']:.1f} ثانیه")
        print("\n📄 فایل‌های خروجی:")
        if isinstance(result, dict):
            print(f"- {result.get('text_file')}: متن ساده")
            print(f"- {result.get('json_file')}: اطلاعات کامل")
        else:
            print("- transcript.txt: متن ساده")
            print("- transcript.json: اطلاعات کامل")
        print("\n💡 نکات:")
        print("- کیفیت تشخیص به کیفیت صدا بستگی دارد")
        print("- برای ویدیوهای فارسی، بهترین نتیجه را خواهید گرفت")
        print("- فایل‌های طولانی ممکن است زمان بیشتری نیاز داشته باشند")
        print("- زمان دانلود به سرعت اینترنت بستگی دارد")
        print("- زمان تبدیل گفتار به تعداد قطعات صوتی بستگی دارد")
    else:
        print("\n❌ خطا در فرآیند تبدیل")
        print(f"⏱️  زمان صرف شده: {total_overall_time:.1f} ثانیه")
        print()
        print("🔧 راه‌حل‌های ممکن:")
        print("1. اتصال اینترنت خود را بررسی کنید")
        print("2. آدرس YouTube را دوباره بررسی کنید")
        print("3. ویدیو باید عمومی باشد (نه خصوصی)")

if __name__ == "__main__":
    main()

