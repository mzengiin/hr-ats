# CVFlow Development Environment Stop Script

Write-Host "🛑 Stopping CVFlow Development Environment..." -ForegroundColor Yellow

# Stop containers
docker-compose -f docker-compose.desktop.yml down

Write-Host "✅ CVFlow Development Environment stopped" -ForegroundColor Green

# Optional: Clean up if requested
if ($args -contains "--clean") {
    Write-Host "Cleaning up volumes and images..." -ForegroundColor Yellow
    docker-compose -f docker-compose.desktop.yml down -v
    docker system prune -f
    Write-Host "✅ Cleanup completed" -ForegroundColor Green
}
