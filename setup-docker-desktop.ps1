# CVFlow Docker Desktop Setup Script
# This script sets up CVFlow for Docker Desktop on Windows

Write-Host "🚀 CVFlow Docker Desktop Setup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if Docker Desktop is installed
Write-Host "Checking Docker Desktop installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop not found. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "Download from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Desktop is running
Write-Host "Checking Docker Desktop status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Create environment file
Write-Host "Creating environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists. Creating backup..." -ForegroundColor Yellow
    Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
}

if (Test-Path "env.desktop.example") {
    Copy-Item "env.desktop.example" ".env"
    Write-Host "✅ Environment file created" -ForegroundColor Green
} else {
    Write-Host "❌ env.desktop.example not found" -ForegroundColor Red
    exit 1
}

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
$directories = @("logs", "backups", "data\postgres")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Set execution policy for PowerShell scripts
Write-Host "Setting PowerShell execution policy..." -ForegroundColor Yellow
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ PowerShell execution policy set" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not set execution policy. You may need to run scripts manually." -ForegroundColor Yellow
}

# Test Docker Compose
Write-Host "Testing Docker Compose..." -ForegroundColor Yellow
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is working" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start the development environment:" -ForegroundColor White
Write-Host "   .\start-dev.bat" -ForegroundColor Gray
Write-Host "   or" -ForegroundColor Gray
Write-Host "   .\scripts\start-dev.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Backend: http://localhost:8001" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8001/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "3. For more information, see DOCKER_DESKTOP_GUIDE.md" -ForegroundColor White
