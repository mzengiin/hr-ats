# CVFlow Database Backup Script

param(
    [string]$BackupPath = ".\backups"
)

Write-Host "💾 Creating database backup..." -ForegroundColor Yellow

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force
}

# Generate backup filename with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$BackupPath\cvflow_backup_$timestamp.sql"

# Create backup
docker-compose -f docker-compose.desktop.yml exec -T db pg_dump -U cvflow_user -d cvflow_db > $backupFile

if (Test-Path $backupFile) {
    Write-Host "✅ Database backup created: $backupFile" -ForegroundColor Green
} else {
    Write-Host "❌ Backup failed" -ForegroundColor Red
}
