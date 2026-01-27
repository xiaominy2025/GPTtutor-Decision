# predeploy_check.ps1
param(
  [string]$CourseDir = "courses\decision",
  [string]$MetaFile = "base_metadata.json",
  [string]$FaissFile = "vector_index.faiss"
)

$ErrorActionPreference = "Stop"

function Md5([string]$path){
  if (!(Test-Path $path)) { return "" }
  $md5 = [System.Security.Cryptography.MD5]::Create()
  $stream = [System.IO.File]::OpenRead($path)
  try {
    $hash = $md5.ComputeHash($stream)
    ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
  } finally { $stream.Dispose(); $md5.Dispose() }
}

Write-Host "== Predeploy checks ==" -ForegroundColor Cyan

# 1) Files exist
$metaPath = Join-Path $CourseDir $MetaFile
$faissPath = Join-Path $CourseDir $FaissFile

if (!(Test-Path $metaPath)) { throw "Missing file: $metaPath" }
if (!(Test-Path $faissPath)) { throw "Missing file: $faissPath" }

# 2) Non-empty
if ((Get-Item $metaPath).Length -le 2) { throw "Empty or tiny: $metaPath" }
if ((Get-Item $faissPath).Length -le 2) { throw "Empty or tiny: $faissPath" }

# 3) JSON valid
try {
  $json = Get-Content $metaPath -Raw | ConvertFrom-Json
} catch {
  throw "Invalid JSON in $metaPath : $($_.Exception.Message)"
}

# 4) Env var
if (-not $env:OPENAI_API_KEY) {
  throw "OPENAI_API_KEY is not set in your environment."
}

# 5) Fingerprints
$metaMd5 = Md5 $metaPath
$faissMd5 = Md5 $faissPath

Write-Host "OK: $metaPath ($(Get-Item $metaPath).Length bytes) md5=$metaMd5" -ForegroundColor Green
Write-Host "OK: $faissPath ($(Get-Item $faissPath).Length bytes) md5=$faissMd5" -ForegroundColor Green
Write-Host "OPENAI_API_KEY present." -ForegroundColor Green
Write-Host "Predeploy checks passed." -ForegroundColor Green
