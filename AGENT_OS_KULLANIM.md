# Agent OS Kullanım Kılavuzu

## 🎉 Agent OS Başarıyla Entegre Edildi!

Projenize Agent OS entegre edildi ve artık spec-driven agentic development kullanabilirsiniz.

## 📁 Proje Yapısı

```
agent deneme/
├── .agent-os/                    # Agent OS dosyaları
│   ├── instructions/             # Agent talimatları
│   │   ├── core/                # Ana komutlar
│   │   └── meta/                # Meta talimatlar
│   └── standards/               # Geliştirme standartları
├── .cursor/                     # Cursor entegrasyonu
│   └── rules/                   # Cursor komut kuralları
├── examples/                    # Örnek kullanımlar
├── agent.js                     # Agent OS API
├── index.js                     # Ana uygulama
└── package.json                 # Proje bağımlılıkları
```

## 🚀 Kullanım

### Cursor'da Komut Kullanımı

Cursor'da aşağıdaki komutları kullanabilirsiniz:

#### 1. **@plan-product** - Yeni Ürün Planlama
- Yeni bir ürün için misyon, tech stack ve roadmap oluşturur
- Kullanım: `@plan-product` yazın ve talimatları takip edin

#### 2. **@analyze-product** - Mevcut Ürün Analizi
- Mevcut kodunuzu analiz eder ve Agent OS'u kurar
- Kullanım: `@analyze-product` yazın

#### 3. **@create-spec** - Özellik Spesifikasyonu
- Yeni bir özellik için detaylı spesifikasyon oluşturur
- Kullanım: `@create-spec` yazın

#### 4. **@create-tasks** - Görev Listesi
- Spesifikasyondan görev listesi oluşturur
- Kullanım: `@create-tasks` yazın

#### 5. **@execute-tasks** - Görevleri Çalıştır
- Görevleri sırayla çalıştırır ve kod üretir
- Kullanım: `@execute-tasks` yazın

## 📋 Örnek Workflow

### 1. Yeni Özellik Ekleme

```bash
# 1. Özellik spesifikasyonu oluştur
@create-spec

# 2. Görev listesi oluştur
@create-tasks

# 3. Görevleri çalıştır
@execute-tasks
```

### 2. Mevcut Projeyi Analiz Etme

```bash
# Mevcut kodunuzu analiz et ve Agent OS'u kur
@analyze-product
```

## 🔧 Agent OS API Kullanımı

### Programatik Kullanım

```javascript
const AgentOS = require('./agent');

// Agent OS'u başlat
const agentOS = new AgentOS();

// Yeni agent oluştur
const agentId = agentOS.createAgent('Web Scraper', 'web-scraper', {
    maxConcurrent: 3,
    delay: 1000
});

// Agent çalıştır
agentOS.runAgent(agentId, {
    url: 'https://example.com',
    selector: '.content'
});
```

### API Endpoints

- `GET /` - Ana sayfa
- `POST /agents` - Yeni agent oluştur
- `GET /agents` - Agent listesi
- `POST /agents/:id/run` - Agent çalıştır
- `GET /agents/:id/status` - Agent durumu

## 📚 Dosya Yapısı

### .agent-os/ klasörü
- **instructions/**: Agent talimatları ve komutları
- **standards/**: Kod standartları ve best practices

### .cursor/ klasörü
- **rules/**: Cursor için komut kuralları (.mdc dosyaları)

## 🎯 Agent Tipleri

1. **web-scraper**: Web sayfalarından veri çıkarma
2. **data-processor**: Veri işleme ve analiz
3. **api-caller**: Harici API çağrıları
4. **generic**: Genel amaçlı görevler

## 📖 Daha Fazla Bilgi

- [Agent OS Resmi Dokümantasyonu](https://buildermethods.com/agent-os)
- [Builder Methods](https://buildermethods.com)
- [GitHub Repository](https://github.com/buildermethods/agent-os)

## 🆘 Yardım

Herhangi bir sorunuz varsa:
1. Cursor'da `@plan-product` komutunu deneyin
2. `examples/example-usage.js` dosyasını inceleyin
3. Agent OS dokümantasyonunu kontrol edin

---

**Agent OS ile geliştirme yapmaya hazırsınız! 🚀**
