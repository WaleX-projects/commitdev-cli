$ErrorActionPreference = "Stop"

# ==========================================
# Configuration
# ==========================================

$Repo = "WaleX-projects/commitdev-cli"
$BinaryName = "commitdev.exe"
$AssetName = "commitdev-windows.exe"

$InstallDirectory = Join-Path $env:LOCALAPPDATA "CommitDev"
$BinaryPath = Join-Path $InstallDirectory $BinaryName

Write-Host ""
Write-Host "CommitDev • Installer" -ForegroundColor Green
Write-Host "──────────────────────────────────────────────────"

# ==========================================
# Get Latest Release
# ==========================================

Write-Host "  › Checking latest release..."

try {
    $Release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
    $Version = $Release.tag_name

    Write-Host "  › Found release $Version"

    $DownloadUrl = "https://github.com/$Repo/releases/download/$Version/$AssetName"
}
catch {
    Write-Host ""
    Write-Host "✕ Failed to retrieve the latest release." -ForegroundColor Red
    exit 1
}

# ==========================================
# Create Install Directory
# ==========================================

if (!(Test-Path $InstallDirectory)) {
    Write-Host "  › Creating installation directory..."
    New-Item -ItemType Directory -Path $InstallDirectory | Out-Null
}

# ==========================================
# Download Binary
# ==========================================

Write-Host "  › Downloading CommitDev..."

try {
    Invoke-WebRequest `
        -Uri $DownloadUrl `
        -OutFile $BinaryPath
}
catch {
    Write-Host ""
    Write-Host "✕ Failed to download CommitDev." -ForegroundColor Red
    exit 1
}

# ==========================================
# Add To PATH
# ==========================================

Write-Host "  › Checking PATH..."

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($UserPath -notlike "*$InstallDirectory*") {

    [Environment]::SetEnvironmentVariable(
        "Path",
        "$UserPath;$InstallDirectory",
        "User"
    )

    Write-Host "  ✓ Added CommitDev to PATH" -ForegroundColor Green
}
else {
    Write-Host "  › CommitDev is already in PATH."
}

# ==========================================
# Initialize CommitDev
# ==========================================

Write-Host ""
Write-Host "Initializing CommitDev..."

try {
    & $BinaryPath setup
}
catch {
    Write-Host ""
    Write-Host "✕ Installation completed, but setup failed." -ForegroundColor Yellow
}

# ==========================================
# Finished
# ==========================================

Write-Host ""
Write-Host "✓ CommitDev installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host ""
Write-Host ""