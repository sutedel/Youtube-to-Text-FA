@echo off
REM ============================================================
REM  Master sequential runner — survives terminal/Claude close.
REM  1) Finishes playlist 1 (urls.txt, resume-safe, skips done)
REM  2) Then runs the queue (queue_next.txt): missed videos + playlist 2
REM  Launched detached via Start-Process; logs to batch_run*.log.
REM ============================================================
cd /d "%~dp0"
chcp 65001 >nul
set WHISPER_MODEL=large-v3
set WHISPER_DEVICE=auto
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo [master] %DATE% %TIME% started >> master.log

echo [master] %DATE% %TIME% running playlist 1 (urls.txt) >> master.log
".venv\Scripts\python.exe" -u transcribe_all.py urls.txt >> batch_run.log 2>&1

echo [master] %DATE% %TIME% running queue (queue_next.txt) >> master.log
".venv\Scripts\python.exe" -u transcribe_all.py queue_next.txt >> batch_run_2.log 2>&1

echo [master] %DATE% %TIME% ALL DONE >> master.log
echo DONE> master_done.flag
