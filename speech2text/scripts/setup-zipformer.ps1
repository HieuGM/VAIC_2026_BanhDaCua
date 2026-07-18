$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ServiceDir = Join-Path $ProjectRoot "zipformer-service"
$VenvDir = Join-Path $ServiceDir ".venv"
$ModelsDir = Join-Path $ServiceDir "models"
$ToolsDir = Join-Path $ProjectRoot "tools"
$FfmpegDir = Join-Path $ToolsDir "ffmpeg"
$ModelName = "sherpa-onnx-zipformer-vi-30M-int8-2026-02-09"
$ModelDir = Join-Path $ModelsDir $ModelName
$ModelArchive = Join-Path $ModelsDir "$ModelName.tar.bz2"
$ModelUrl = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/$ModelName.tar.bz2"
$FfmpegZip = Join-Path $ToolsDir "ffmpeg-release-essentials.zip"
$FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

function Test-ModelReady {
  return (
    (Test-Path (Join-Path $ModelDir "encoder.int8.onnx")) -and
    (Test-Path (Join-Path $ModelDir "decoder.onnx")) -and
    (Test-Path (Join-Path $ModelDir "joiner.int8.onnx")) -and
    (Test-Path (Join-Path $ModelDir "tokens.txt"))
  )
}

function Get-PortableFfmpeg {
  if (-not (Test-Path $FfmpegDir)) {
    return $null
  }

  return Get-ChildItem -LiteralPath $FfmpegDir -Recurse -Filter "ffmpeg.exe" |
    Select-Object -First 1
}

New-Item -ItemType Directory -Force -Path $ServiceDir, $ModelsDir, $ToolsDir, $FfmpegDir | Out-Null

if (-not (Test-Path $VenvDir)) {
  Write-Host "Creating Python virtual environment..."
  python -m venv $VenvDir
}

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "Installing Python dependencies..."
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r (Join-Path $ServiceDir "requirements.txt")

if (-not (Get-PortableFfmpeg)) {
  Write-Host "Downloading portable FFmpeg..."
  Invoke-WebRequest -Uri $FfmpegUrl -OutFile $FfmpegZip
  Expand-Archive -LiteralPath $FfmpegZip -DestinationPath $FfmpegDir -Force
  Remove-Item -LiteralPath $FfmpegZip -Force
} else {
  Write-Host "Portable FFmpeg already exists."
}

if (-not (Test-ModelReady)) {
  Write-Host "Downloading Zipformer Vietnamese model..."
  Invoke-WebRequest -Uri $ModelUrl -OutFile $ModelArchive
  tar -xf $ModelArchive -C $ModelsDir
  Remove-Item -LiteralPath $ModelArchive -Force
} else {
  Write-Host "Zipformer model already exists."
}

if (-not (Test-ModelReady)) {
  throw "Zipformer model setup failed. Missing one or more required model files."
}

$FfmpegExe = Get-PortableFfmpeg
if (-not $FfmpegExe) {
  throw "Portable FFmpeg setup failed. ffmpeg.exe was not found."
}

Write-Host ""
Write-Host "Zipformer setup complete."
Write-Host "Model: $ModelDir"
Write-Host "FFmpeg: $($FfmpegExe.FullName)"
Write-Host "Run service: npm run zipformer:service"
