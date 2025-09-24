# =======================================
# Rebuild Metadata & Bake for Deployment
# Generates:
#   - courses/decision/base_metadata.json (full backend baked metadata)
#   - public/courses/decision/ui_metadata.json (lightweight frontend metadata)
# =======================================

# Ensure we're in the project root
Set-Location "C:\Users\xmkya\Documents\Xiaomin Folder\ThinkPal Project\GPTTutor-Decision"

Write-Host "=== Step 1: Rebuilding comprehensive metadata locally ==="

# 1. Run your Python metadata rebuild script
# Replace with your actual rebuild command if different
python tools/rebuild_metadata.py --course decision

# Paths
$fullSource = "courses\decision\metadata.json"
$backendTarget = "courses\decision\base_metadata.json"
$frontendTarget = "public\courses\decision\ui_metadata.json"

# 2. Validate source exists
if (-Not (Test-Path $fullSource)) {
    Write-Error "❌ No rebuilt metadata.json found at $fullSource"
    exit 1
}

# 3. Validate size
$fileSizeKB = (Get-Item $fullSource).Length / 1KB
if ($fileSizeKB -lt 10) {
    Write-Error "❌ metadata.json is too small (<10 KB) — rebuild may have failed."
    exit 1
}

# 4. Copy to backend baked metadata
Copy-Item $fullSource $backendTarget -Force
Write-Host "✅ Copied metadata.json to $backendTarget"

# 5. Validate backend JSON
try {
    $json = Get-Content $backendTarget -Raw | ConvertFrom-Json
    Write-Host "✅ base_metadata.json is valid JSON."
} catch {
    Write-Error "❌ base_metadata.json is not valid JSON."
    exit 1
}

# 6. Generate lightweight frontend metadata
try {
    $uiMetadata = [PSCustomObject]@{
        course_id   = $json.course_id
        title       = $json.title
        description = $json.description
        sections    = $json.sections
    }

    # Ensure frontend folder exists
    $frontendDir = Split-Path $frontendTarget
    if (-Not (Test-Path $frontendDir)) {
        New-Item -ItemType Directory -Path $frontendDir -Force | Out-Null
    }

    $uiMetadata | ConvertTo-Json -Depth 3 | Set-Content $frontendTarget -Encoding UTF8
    Write-Host "✅ Created lightweight UI metadata at $frontendTarget"
} catch {
    Write-Error "❌ Failed to generate UI metadata: $_"
    exit 1
}

Write-Host "=== Metadata bake completed successfully ==="
