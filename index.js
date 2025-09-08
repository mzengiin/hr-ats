const AgentOS = require('./agent');

// Agent OS'u başlat
const agentOS = new AgentOS();

// Örnek agentlar oluştur
console.log('Agent OS başlatılıyor...');

// Web scraper agent
const webScraperId = agentOS.createAgent('Web Scraper', 'web-scraper', {
    maxConcurrent: 3,
    delay: 1000
});

// Data processor agent
const dataProcessorId = agentOS.createAgent('Data Processor', 'data-processor', {
    batchSize: 100,
    timeout: 30000
});

// API caller agent
const apiCallerId = agentOS.createAgent('API Caller', 'api-caller', {
    retryAttempts: 3,
    timeout: 5000
});

console.log('Örnek agentlar oluşturuldu:');
console.log(`- Web Scraper: ${webScraperId}`);
console.log(`- Data Processor: ${dataProcessorId}`);
console.log(`- API Caller: ${apiCallerId}`);

// Agent OS'u başlat
agentOS.start();
