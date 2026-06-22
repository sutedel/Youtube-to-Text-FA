# Master sequential runner — detached, survives terminal/Claude close.
# Runs playlist 1 (urls.txt) then the queue (queue_next.txt: missed + playlist 2),
# and RETRIES in passes so transient YouTube/network errors over a long job get
# re-attempted (the batch is resume-safe: done videos are skipped each pass).
Set-Location "c:\forex\texttrex\Youtube-to-Text-FA"
$env:WHISPER_MODEL = "large-v3"
$env:WHISPER_DEVICE = "auto"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$py = ".\.venv\Scripts\python.exe"

function Log($m) { "[master] $(Get-Date -Format o) $m" | Out-File master.log -Append -Encoding utf8 }

Log "started"
$maxPasses = 6
for ($i = 1; $i -le $maxPasses; $i++) {
    Log "pass $i : playlist 1 (urls.txt)"
    & $py -u transcribe_all.py urls.txt *>> batch_run.log

    Log "pass $i : queue (queue_next.txt)"
    & $py -u transcribe_all.py queue_next.txt *>> batch_run_2.log

    $left = (& $py -u check_remaining.py 2>$null | Select-Object -Last 1)
    Log "pass $i complete; remaining videos without transcript = $left"
    if ("$left" -eq "0") { break }
    if ($i -lt $maxPasses) { Start-Sleep -Seconds 180 }
}
Log "ALL DONE"
"DONE" | Out-File master_done.flag -Encoding utf8
