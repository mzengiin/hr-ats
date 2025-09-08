# CVFlow Development Environment Logs Script

param(
    [string]$Service = "all"
)

Write-Host "📋 Showing CVFlow logs..." -ForegroundColor Yellow

if ($Service -eq "all") {
    docker-compose -f docker-compose.desktop.yml logs -f
} else {
    docker-compose -f docker-compose.desktop.yml logs -f $Service
}
