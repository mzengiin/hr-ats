@echo off
echo ========================================
echo HIZLI CORS COZUM - RESTART
echo ========================================

echo.
echo 1. Backend container'ini durduruyor...
docker stop agentdeneme-backend-1

echo.
echo 2. Backend container'ini kaldırıyor...
docker rm agentdeneme-backend-1

echo.
echo 3. Backend'i yeniden başlatıyor...
docker-compose up -d backend

echo.
echo 4. Backend'in başlamasını bekliyor...
timeout /t 15 /nobreak

echo.
echo 5. Backend durumunu kontrol ediyor...
docker logs agentdeneme-backend-1 --tail 10

echo.
echo ========================================
echo RESTART TAMAMLANDI!
echo ========================================
echo.
echo Şimdi frontend'de kullanıcı yönetimi sayfasını test edin.
echo CORS hatası artık almamalısınız.
echo.
pause
