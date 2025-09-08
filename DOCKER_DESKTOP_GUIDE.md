# CVFlow Docker Desktop Guide

Bu rehber, CVFlow projesini Windows üzerinde Docker Desktop kullanarak çalıştırmanız için gerekli adımları içerir.

## Gereksinimler

### Sistem Gereksinimleri
- Windows 10/11 (64-bit)
- En az 8GB RAM
- En az 20GB boş disk alanı
- WSL2 desteği

### Yazılım Gereksinimleri
- Docker Desktop for Windows
- Git for Windows
- PowerShell 5.1+ (Windows 10/11 ile birlikte gelir)

## Kurulum

### 1. Docker Desktop Kurulumu

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) indirin
2. Kurulum dosyasını çalıştırın
3. Kurulum sırasında "Use WSL 2 instead of Hyper-V" seçeneğini işaretleyin
4. Bilgisayarı yeniden başlatın

### 2. WSL2 Kurulumu (Gerekirse)

```powershell
# PowerShell'i yönetici olarak çalıştırın
wsl --install
```

### 3. Proje Kurulumu

```powershell
# Projeyi klonlayın
git clone <repository-url>
cd cvflow

# Environment dosyasını kopyalayın
Copy-Item .env.desktop .env
```

## Hızlı Başlangıç

### Geliştirme Ortamını Başlatma

```powershell
# PowerShell'i proje dizininde açın
.\scripts\start-dev.ps1
```

### Geliştirme Ortamını Durdurma

```powershell
.\scripts\stop-dev.ps1
```

### Ortamı Yeniden Başlatma

```powershell
.\scripts\restart-dev.ps1
```

### Logları Görüntüleme

```powershell
# Tüm servislerin logları
.\scripts\logs.ps1

# Belirli bir servisin logları
.\scripts\logs.ps1 -Service backend
.\scripts\logs.ps1 -Service frontend
.\scripts\logs.ps1 -Service db
```

## Gelişmiş Kullanım

### Temiz Kurulum

```powershell
# Eski verileri temizleyerek başlat
.\scripts\start-dev.ps1 --clean
```

### Demo Kullanıcı Oluşturma

```powershell
# Demo kullanıcı ile başlat
.\scripts\start-dev.ps1 --demo
```

### Veritabanı Yedekleme

```powershell
# Veritabanını yedekle
.\scripts\backup-db.ps1

# Belirli bir dizine yedekle
.\scripts\backup-db.ps1 -BackupPath "C:\Backups"
```

## Servisler

### Erişim Adresleri
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Dokümantasyonu**: http://localhost:8001/docs
- **Veritabanı**: localhost:5432

### Servis Yönetimi

```powershell
# Servis durumunu kontrol et
docker-compose -f docker-compose.desktop.yml ps

# Belirli bir servisi yeniden başlat
docker-compose -f docker-compose.desktop.yml restart backend

# Belirli bir servisi durdur
docker-compose -f docker-compose.desktop.yml stop frontend
```

## Geliştirme

### Backend Geliştirme

```powershell
# Backend container'ına bağlan
docker-compose -f docker-compose.desktop.yml exec backend bash

# Veritabanı migration'larını çalıştır
docker-compose -f docker-compose.desktop.yml exec backend alembic upgrade head

# Yeni migration oluştur
docker-compose -f docker-compose.desktop.yml exec backend alembic revision --autogenerate -m "Description"

# Testleri çalıştır
docker-compose -f docker-compose.desktop.yml exec backend python -m pytest
```

### Frontend Geliştirme

```powershell
# Frontend container'ına bağlan
docker-compose -f docker-compose.desktop.yml exec frontend sh

# Yeni paket yükle
docker-compose -f docker-compose.desktop.yml exec frontend npm install package-name

# Testleri çalıştır
docker-compose -f docker-compose.desktop.yml exec frontend npm test
```

## Sorun Giderme

### Docker Desktop Çalışmıyor

1. Docker Desktop'ı yönetici olarak çalıştırın
2. WSL2'nin etkin olduğundan emin olun
3. Windows özelliklerinde "Virtual Machine Platform" ve "Windows Subsystem for Linux" etkinleştirin

### Port Çakışması

```powershell
# Kullanılan portları kontrol et
netstat -ano | findstr :3000
netstat -ano | findstr :8001
netstat -ano | findstr :5432

# Port kullanan işlemi sonlandır
taskkill /PID <process_id> /F
```

### Container Başlamıyor

```powershell
# Container loglarını kontrol et
docker-compose -f docker-compose.desktop.yml logs backend
docker-compose -f docker-compose.desktop.yml logs frontend
docker-compose -f docker-compose.desktop.yml logs db

# Container'ları yeniden oluştur
docker-compose -f docker-compose.desktop.yml up --build --force-recreate
```

### Veritabanı Bağlantı Sorunu

```powershell
# Veritabanı container'ının durumunu kontrol et
docker-compose -f docker-compose.desktop.yml ps db

# Veritabanı loglarını kontrol et
docker-compose -f docker-compose.desktop.yml logs db

# Veritabanını yeniden başlat
docker-compose -f docker-compose.desktop.yml restart db
```

### Performans Sorunları

1. Docker Desktop ayarlarında RAM miktarını artırın (en az 4GB)
2. WSL2 backend kullanın
3. Antivirus yazılımını proje dizininden hariç tutun

## Üretim Ortamı

### Üretim Ortamını Başlatma

```powershell
# Üretim environment dosyasını oluştur
Copy-Item .env.desktop .env.production

# Üretim ortamını başlat
docker-compose -f docker-compose.prod.yml up -d
```

### Üretim Ortamını Durdurma

```powershell
docker-compose -f docker-compose.prod.yml down
```

## Faydalı Komutlar

```powershell
# Tüm container'ları temizle
docker system prune -a

# Kullanılmayan volume'ları temizle
docker volume prune

# Kullanılmayan image'ları temizle
docker image prune -a

# Docker sistem bilgilerini görüntüle
docker system df

# Container kaynak kullanımını görüntüle
docker stats
```

## Güvenlik

### Environment Değişkenleri

- `.env` dosyasını asla Git'e commit etmeyin
- Üretim ortamında güçlü şifreler kullanın
- `SECRET_KEY`'i düzenli olarak değiştirin

### Veritabanı Güvenliği

- Üretim ortamında veritabanı şifrelerini güçlü yapın
- Veritabanı erişimini sınırlayın
- Düzenli yedekleme yapın

## Destek

Sorun yaşarsanız:

1. Bu rehberi kontrol edin
2. Docker Desktop loglarını inceleyin
3. Proje dokümantasyonunu kontrol edin
4. GitHub issues'da arama yapın

## Faydalı Linkler

- [Docker Desktop Documentation](https://docs.docker.com/desktop/windows/)
- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
