# ==================================================
# CommitDev Installer
# ==================================================

$Repo = "WaleX-projects/commitdev-cli"
$BinaryName = "commitdev.exe"

$InstallDir = Join-Path $env:LOCALAPPDATA "CommitDev"
$BinaryPath = Join-Path $InstallDir $BinaryName
$TempFile = Join-Path $env:TEMP $BinaryName

Write-Host ""
Write-Host "CommitDev • Installer" -ForegroundColor Green
Write-Host "──────────────────────────────────────────────────"

# ==================================================
# Detect Platform
# ==================================================

Write-Host ""
Write-Host "• Detecting platform..."

Write-Host "  ✓ Windows" -ForegroundColor Green

# ==================================================
# Check Existing Installation
# ==================================================

Write-Host ""
Write-Host "• Checking existing installation..."

$CurrentVersion = $null

if (Test-Path $BinaryPath) {

    try {

        $VersionOutput = & $BinaryPath --version

        if ($VersionOutput -match "v?(\d+\.\d+\.\d+)") {
            $CurrentVersion = "v$($Matches[1])"
            Write-Host "  ✓ Found CommitDev $CurrentVersion" -ForegroundColor Green
        }
        else {
            Write-Host "  › Existing installation detected."
        }

    }
    catch {
        Write-Host "  › Existing installation detected."
    }

}
else {

    Write-Host "  › CommitDev is not installed."

}

# ==================================================
# Latest Release
# ==================================================

Write-Host ""
Write-Host "• Checking latest release..."

try {

    $Release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
    $LatestVersion = $Release.tag_name

}
catch {

    Write-Host "  ✕ Failed to determine the latest release." -ForegroundColor Red
    exit 1

}

Write-Host "  ✓ $LatestVersion" -ForegroundColor Green

# ==================================================
# Already Up To Date?
# ==================================================

if ($CurrentVersion -eq $LatestVersion) {

    Write-Host ""
    Write-Host "──────────────────────────────────────────────────"
    Write-Host "✓ You're already running the latest version." -ForegroundColor Green
    exit 0

}

# ==================================================
# Download
# ==================================================

Write-Host ""

if ($CurrentVersion) {
    Write-Host "• Updating CommitDev..."
}
else {
    Write-Host "• Installing CommitDev..."
}

Write-Host "  › Downloading release..."

$DownloadUrl = "https://github.com/$Repo/releases/download/$LatestVersion/commitdev-windows.exe"

try {

    Invoke-WebRequest `
        -Uri $DownloadUrl `
        -OutFile $TempFile

}
catch {

    Write-Host "  ✕ Failed to download CommitDev." -ForegroundColor Red
    exit 1

}

Write-Host "  ✓ Download complete." -ForegroundColor Green

# ==================================================
# Install
# ==================================================

Write-Host "  › Installing executable..."

if (!(Test-Path $InstallDir)) {
    New-Item `
        -ItemType Directory `
        -Path $InstallDir | Out-Null
}

Move-Item `
    -Force `
    $TempFile `
    $BinaryPath

Write-Host "  ✓ Installed to $BinaryPath" -ForegroundColor Green

# ==================================================
# Add To PATH
# ==================================================

$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($UserPath -notlike "*$InstallDir*") {

    [Environment]::SetEnvironmentVariable(
        "Path",
        "$UserPath;$InstallDir",
        "User"
    )

    Write-Host "  ✓ Added CommitDev to your PATH." -ForegroundColor Green

}

# ==================================================
# Initialize
# ==================================================

Write-Host ""
Write-Host "• Initializing workspace..."

& $BinaryPath setup

Write-Host "  ✓ Workspace initialized." -ForegroundColor Green

# ==================================================
# Finished
# ==================================================

Write-Host ""
Write-Host "──────────────────────────────────────────────────"
Write-Host "✓ CommitDev $LatestVersion is ready." -ForegroundColor Green

Write-Host ""
Write-Host "Run:"
Write-Host ""
Write-Host "  commitdev login"

Write-Host ""
Write-Host "If this is your first installation, restart PowerShell or Windows Terminal if the 'commitdev' command isn't available immediately."