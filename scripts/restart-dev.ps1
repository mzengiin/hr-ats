# CVFlow Development Environment Restart Script

Write-Host "🔄 Restarting CVFlow Development Environment..." -ForegroundColor Yellow

# Stop current environment
& .\scripts\stop-dev.ps1

# Wait a moment
Start-Sleep -Seconds 3

# Start environment
& .\scripts\start-dev.ps1 @args
