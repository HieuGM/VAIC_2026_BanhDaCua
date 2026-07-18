$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ServiceDir = Join-Path $ProjectRoot "zipformer-service"
$PythonExe = Join-Path $ServiceDir ".venv\Scripts\python.exe"
$FfmpegRoot = Join-Path $ProjectRoot "tools\ffmpeg"

if (-not (Test-Path $PythonExe)) {
  throw "Python virtual environment not found. Run npm run zipformer:setup first."
}

$FfmpegExe = Get-ChildItem -LiteralPath $FfmpegRoot -Recurse -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue |
  Select-Object -First 1

if (-not $FfmpegExe) {
  throw "Portable FFmpeg not found. Run npm run zipformer:setup first."
}

$env:ZIPFORMER_FFMPEG_PATH = $FfmpegExe.FullName

Push-Location $ServiceDir
try {
  & $PythonExe -m uvicorn app:app --host 127.0.0.1 --port 8001
} finally {
  Pop-Location
}
