@echo off
REM ============================================================
REM  اجرای کامل تبدیل ویدیوهای یوتیوب به متن (برای لپ‌تاپ دارای GPU)
REM  این فایل: محیط مجازی می‌سازد، نیازمندی‌ها را نصب می‌کند،
REM  کتابخانه‌های CUDA را برای GPU نصب می‌کند، و همه‌ی لینک‌های
REM  داخل urls.txt را تبدیل می‌کند.
REM ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================================
echo   تبدیل انبوه ویدیو به متن (Whisper)
echo ============================================================

REM --- بررسی نصب بودن Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [خطا] Python پیدا نشد. لطفا Python 3.10+ را نصب کنید و دوباره اجرا کنید.
    echo        https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- بررسی نصب بودن ffmpeg ---
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo [هشدار] ffmpeg پیدا نشد. برای پردازش صدا لازم است.
    echo          نصب با:  winget install Gyan.FFmpeg
    echo          سپس پنجره را ببندید و دوباره اجرا کنید.
    pause
)

REM --- ساخت محیط مجازی در صورت نبودن ---
if not exist ".venv\Scripts\python.exe" (
    echo در حال ساخت محیط مجازی...
    python -m venv .venv
)

set "PY=.venv\Scripts\python.exe"

echo در حال نصب نیازمندی‌ها...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt

REM --- کتابخانه‌های CUDA برای اجرای Whisper روی GPU ---
echo در حال نصب کتابخانه‌های CUDA برای GPU...
"%PY%" -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12

REM --- تنظیمات موتور ---
set WHISPER_MODEL=large-v3
set WHISPER_DEVICE=auto
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo.
echo شروع پردازش همه‌ی لینک‌های داخل urls.txt ...
echo (اگر GPU انویدیا فعال باشد سریع است؛ روی CPU بسیار کند می‌شود)
echo.

"%PY%" transcribe_all.py urls.txt

echo.
echo ============================================================
echo   پردازش تمام شد. خروجی‌ها در پوشه‌ی output هستند.
echo ============================================================
pause
endlocal
