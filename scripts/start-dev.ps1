# CVFlow Development Environment Startup Script
# This script starts the development environment using Docker Desktop

Write-Host "🚀 Starting CVFlow Development Environment..." -ForegroundColor Green

# Check if Docker Desktop is running
Write-Host "Checking Docker Desktop status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.desktop.yml down

# Remove old volumes if requested
if ($args -contains "--clean") {
    Write-Host "Cleaning up old volumes..." -ForegroundColor Yellow
    docker-compose -f docker-compose.desktop.yml down -v
    docker system prune -f
}

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.desktop.yml up --build -d

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "Checking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.desktop.yml ps

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
docker-compose -f docker-compose.desktop.yml exec backend alembic upgrade head

# Create demo user if requested
if ($args -contains "--demo") {
    Write-Host "Creating demo user..." -ForegroundColor Yellow
    docker-compose -f docker-compose.desktop.yml exec backend python create_demo_user.py
}

Write-Host "🎉 CVFlow Development Environment is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8001" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs: docker-compose -f docker-compose.desktop.yml logs -f" -ForegroundColor Yellow
Write-Host "To stop: docker-compose -f docker-compose.desktop.yml down" -ForegroundColor Yellow
