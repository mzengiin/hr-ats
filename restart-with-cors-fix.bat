@echo off
echo ========================================
echo CORS Sorunu Kalici Cozum - Restart
echo ========================================

echo.
echo 1. Docker container'larini durduruyor...
docker-compose down

echo.
echo 2. Container'ları temizliyor...
docker-compose down --volumes --remove-orphans

echo.
echo 3. Backend container'ini yeniden build ediyor...
docker-compose build backend

echo.
echo 4. Tüm servisleri başlatıyor...
docker-compose up -d

echo.
echo 5. Servislerin başlamasını bekliyor...
timeout /t 10 /nobreak

echo.
echo 6. CORS durumunu kontrol ediyor...
docker logs agentdeneme-backend-1 --tail 20

echo.
echo ========================================
echo CORS Sorunu Cozuldu!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8001
echo.
echo Test etmek için:
echo 1. Frontend'e gidin
echo 2. Kullanici yonetimi sayfasina gidin
echo 3. Artik CORS hatasi almamalisiniz
echo.
pause
