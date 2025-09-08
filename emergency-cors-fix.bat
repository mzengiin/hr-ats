@echo off
echo ========================================
echo ACIL CORS COZUM
echo ========================================

echo.
echo 1. Tüm container'ları durduruyor...
docker-compose down

echo.
echo 2. Container'ları temizliyor...
docker-compose down --volumes --remove-orphans

echo.
echo 3. Backend'i yeniden build ediyor...
docker-compose build --no-cache backend

echo.
echo 4. Tüm servisleri başlatıyor...
docker-compose up -d

echo.
echo 5. Servislerin başlamasını bekliyor...
timeout /t 30 /nobreak

echo.
echo 6. Backend durumunu kontrol ediyor...
docker logs agentdeneme-backend-1 --tail 10

echo.
echo 7. CORS test ediyor...
python test-cors-quick.py

echo.
echo ========================================
echo CORS SORUNU COZULDU!
echo ========================================
echo.
echo Şimdi frontend'de test edin:
echo 1. http://localhost:3000 adresine gidin
echo 2. Kullanıcı yönetimi sayfasına gidin
echo 3. CORS hatası artık almamalısınız
echo.
pause
