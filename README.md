# CVFlow - CV Management System

CVFlow, Python FastAPI backend ve React frontend ile geliştirilmiş kapsamlı bir CV yönetim ve HR süreç otomasyon sistemidir.

## Özellikler

- 👤 Kullanıcı yönetimi ve kimlik doğrulama
- 📄 CV dosya yükleme ve yönetimi
- 🔐 Rol tabanlı erişim kontrolü (RBAC)
- 📊 Dashboard ve raporlama
- 🔄 RESTful API arayüzü
- 🐳 Docker desteği

## Hızlı Başlangıç

### Docker Desktop ile (Önerilen)

1. **Docker Desktop'ı yükleyin**:
   - [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) indirin ve kurun
   - WSL2 desteğini etkinleştirin

2. **Projeyi klonlayın**:
```bash
git clone <repository-url>
cd cvflow
```

3. **Environment dosyasını oluşturun**:
```bash
# Windows PowerShell
Copy-Item env.desktop.example .env

# Linux/Mac
cp env.desktop.example .env
```

4. **Geliştirme ortamını başlatın**:
```powershell
# Windows PowerShell
.\scripts\start-dev.ps1

# Linux/Mac
docker-compose -f docker-compose.desktop.yml up -d
```

5. **Uygulamaya erişin**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Dokümantasyonu: http://localhost:8001/docs

### Manuel Kurulum

1. **Backend kurulumu**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend kurulumu**:
```bash
cd frontend
npm install
npm start
```

3. **Veritabanı kurulumu**:
```bash
# PostgreSQL kurulumu ve migration'lar
cd backend
alembic upgrade head
```

## Kullanım

### Docker Desktop ile Geliştirme

```powershell
# Geliştirme ortamını başlat
.\start-dev.bat

# Veya PowerShell ile
.\scripts\start-dev.ps1

# Ortamı durdur
.\stop-dev.bat

# Ortamı yeniden başlat
.\restart-dev.bat

# Logları görüntüle
.\scripts\logs.ps1
```

### Manuel Geliştirme

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm start
```

### API Kullanımı

#### Yeni Agent Oluşturma
```bash
curl -X POST http://localhost:3000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Agent",
    "type": "web-scraper",
    "config": {
      "maxConcurrent": 3,
      "delay": 1000
    }
  }'
```

#### Agent Listesi
```bash
curl http://localhost:3000/agents
```

#### Agent Çalıştırma
```bash
curl -X POST http://localhost:3000/agents/{agent-id}/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "url": "https://example.com",
      "selector": ".content"
    }
  }'
```

#### Agent Durumu
```bash
curl http://localhost:3000/agents/{agent-id}/status
```

## Agent Tipleri

### Web Scraper
Web sayfalarından veri çıkarma işlemleri için kullanılır.

### Data Processor
Büyük veri setlerini işleme ve analiz etme işlemleri için kullanılır.

### API Caller
Harici API'lere çağrı yapma işlemleri için kullanılır.

### Generic
Genel amaçlı görevler için kullanılır.

## Konfigürasyon

`agent.config.js` dosyasından agent ayarlarını yapılandırabilirsiniz.

## Geliştirme

Projeyi geliştirme modunda çalıştırmak için:

```bash
npm run dev
```

Bu komut nodemon kullanarak dosya değişikliklerini otomatik olarak algılar ve sunucuyu yeniden başlatır.

## Lisans

MIT
