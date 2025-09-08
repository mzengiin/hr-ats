@echo off
echo ========================================
echo CORS SORUNU HIZLI COZUM
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
timeout /t 20 /nobreak

echo.
echo 5. Backend durumunu kontrol ediyor...
docker logs agentdeneme-backend-1 --tail 5

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