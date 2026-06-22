# Master runner for playlist 3 — detached, survives terminal/Claude close.
# Retries in passes so transient YouTube/network errors get re-attempted
# (resume-safe: already-transcribed videos are skipped each pass).
Set-Location "c:\forex\texttrex\Youtube-to-Text-FA"
$env:WHISPER_MODEL = "large-v3"
$env:WHISPER_DEVICE = "auto"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$py = ".\.venv\Scripts\python.exe"

function Log($m) { "[master3] $(Get-Date -Format o) $m" | Out-File master3.log -Append -Encoding utf8 }

Log "started"
$maxPasses = 6
for ($i = 1; $i -le $maxPasses; $i++) {
    Log "pass $i : playlist 3 (playlist3.txt)"
    & $py -u transcribe_all.py playlist3.txt *>> batch_run3.log

    $left = (& $py -u check_remaining.py playlist3.txt 2>$null | Select-Object -Last 1)
    Log "pass $i complete; remaining videos without transcript = $left"
    if ("$left" -eq "0") { break }
    if ($i -lt $maxPasses) { Start-Sleep -Seconds 180 }
}
Log "ALL DONE"
"DONE" | Out-File master3_done.flag -Encoding utf8
