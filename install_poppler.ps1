# PowerShell script to install Poppler for Windows
# Run this script as Administrator

$downloadUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
$tempPath = "$env:TEMP\poppler.zip"
$installPath = "C:\poppler"

Write-Host "Downloading Poppler..." -ForegroundColor Green
try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempPath
    Write-Host "Download completed!" -ForegroundColor Green
} catch {
    Write-Host "Download failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Extracting Poppler..." -ForegroundColor Green
try {
    Expand-Archive -Path $tempPath -DestinationPath $installPath -Force
    Write-Host "Extraction completed!" -ForegroundColor Green
} catch {
    Write-Host "Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Find the bin directory
$binPath = Get-ChildItem -Path $installPath -Recurse -Directory -Name "bin" | Select-Object -First 1
if ($binPath) {
    $fullBinPath = Join-Path $installPath $binPath
    
    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($currentPath -notlike "*$fullBinPath*") {
        $newPath = "$currentPath;$fullBinPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
        Write-Host "Added $fullBinPath to system PATH" -ForegroundColor Green
        Write-Host "Please restart your terminal for PATH changes to take effect." -ForegroundColor Yellow
    } else {
        Write-Host "Poppler bin directory already in PATH" -ForegroundColor Yellow
    }
} else {
    Write-Host "Could not find bin directory in extracted files" -ForegroundColor Red
}

# Clean up
Remove-Item $tempPath -Force -ErrorAction SilentlyContinue
Write-Host "Installation complete!" -ForegroundColor Green
