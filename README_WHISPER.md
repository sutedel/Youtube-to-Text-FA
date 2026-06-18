# موتور تبدیل گفتار به متن (Whisper)

این پروژه به جای Google Web Speech از **faster-whisper** استفاده می‌کند که برای فارسی
محاوره‌ای/با لهجه دقت بسیار بالاتری دارد و با `initial_prompt` واژه‌نامه‌ی تخصصی سبک
تیرکس را می‌گیرد تا اصطلاحات (تیرکس، کندل، اف تی سی، آر تی پی، لگ، بیس...) درست نوشته شوند.

اگر faster-whisper نصب نباشد یا بارگذاری مدل شکست بخورد، به‌صورت خودکار به Google برمی‌گردد.

## نکته‌ی مهم درباره‌ی سرعت

- روی **GPU انویدیا** سریع است (مدل `large-v3` نزدیک یا بهتر از real-time).
- روی **CPU** بسیار کند است — برای ویدیوهای بلند (۶۰+ دقیقه) عملاً چند ساعت طول می‌کشد.
  پس کار انبوه را روی سیستم دارای GPU انویدیا اجرا کنید.

## راه‌اندازی روی لپ‌تاپ گیمینگ (GPU انویدیا)

```powershell
# داخل پوشه‌ی پروژه
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# کتابخانه‌های CUDA لازم برای faster-whisper روی GPU (CUDA 12 / cuDNN 9):
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12

# اجرا (تشخیص GPU خودکار است):
python working_youtube_to_text.py "<YOUTUBE_URL>"
```

اگر تشخیص خودکار GPU را نگرفت، صراحتاً تعیین کنید:

```powershell
$env:WHISPER_DEVICE = "cuda"
$env:WHISPER_COMPUTE_TYPE = "float16"
python working_youtube_to_text.py "<YOUTUBE_URL>"
```

## متغیرهای محیطی (تنظیم بدون تغییر کد)

| متغیر | پیش‌فرض | توضیح |
|-------|---------|-------|
| `WHISPER_MODEL` | `large-v3` | اندازه‌ی مدل: `large-v3` (بهترین) ، `large-v3-turbo` (سریع‌تر، کیفیت نزدیک) ، `medium` ، `small` |
| `WHISPER_DEVICE` | `auto` | `auto` / `cuda` / `cpu` |
| `WHISPER_COMPUTE_TYPE` | خودکار | روی GPU: `float16` ، روی CPU: `int8` |
| `USE_WHISPER` | `1` | با `0` به موتور Google برمی‌گردد |

### گزینه‌ی سریع‌تر روی CPU (اگر مجبور بودید همین‌جا اجرا کنید)

```powershell
$env:WHISPER_MODEL = "large-v3-turbo"   # یا "medium"
python working_youtube_to_text.py --max-minutes 2 "<YOUTUBE_URL>"
```

## تصحیح اصطلاحات

ماژول `persian_domain_corrector.py` بعد از رونویسی، خطاهای قطعیِ ناشی از لهجه را اصلاح
می‌کند (مثل «تیکس»→«تیرکس»، «ftc»→«اف تی سی»، اعداد لاتین→فارسی). برای افزودن تصحیح
جدید، فهرست `_RAW_CORRECTIONS` را در همان فایل ویرایش کنید (محافظه‌کار بماند تا خروجی درست خراب نشود).

## تست سریع

`--max-minutes N` فقط N دقیقه‌ی اول را پردازش می‌کند (برای تست بدون انتظار طولانی).
اولین اجرا مدل را یک‌بار از HuggingFace دانلود می‌کند (large-v3 حدود ۳ گیگابایت) و در کش نگه می‌دارد.
