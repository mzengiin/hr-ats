const axios = require('axios');

// Agent OS API base URL
const API_BASE = 'http://localhost:3000';

class AgentOSClient {
    constructor(baseUrl = API_BASE) {
        this.baseUrl = baseUrl;
    }

    // Yeni agent oluştur
    async createAgent(name, type, config = {}) {
        try {
            const response = await axios.post(`${this.baseUrl}/agents`, {
                name,
                type,
                config
            });
            return response.data;
        } catch (error) {
            console.error('Agent oluşturma hatası:', error.message);
            throw error;
        }
    }

    // Agent listesini al
    async getAgents() {
        try {
            const response = await axios.get(`${this.baseUrl}/agents`);
            return response.data;
        } catch (error) {
            console.error('Agent listesi alma hatası:', error.message);
            throw error;
        }
    }

    // Agent çalıştır
    async runAgent(agentId, task) {
        try {
            const response = await axios.post(`${this.baseUrl}/agents/${agentId}/run`, {
                task
            });
            return response.data;
        } catch (error) {
            console.error('Agent çalıştırma hatası:', error.message);
            throw error;
        }
    }

    // Agent durumunu al
    async getAgentStatus(agentId) {
        try {
            const response = await axios.get(`${this.baseUrl}/agents/${agentId}/status`);
            return response.data;
        } catch (error) {
            console.error('Agent durumu alma hatası:', error.message);
            throw error;
        }
    }
}

// Örnek kullanım
async function example() {
    const client = new AgentOSClient();

    try {
        console.log('Agent OS Client örneği başlatılıyor...\n');

        // 1. Mevcut agentları listele
        console.log('1. Mevcut agentlar:');
        const agents = await client.getAgents();
        console.log(agents);
        console.log('');

        // 2. Yeni bir web scraper agent oluştur
        console.log('2. Yeni web scraper agent oluşturuluyor...');
        const newAgent = await client.createAgent('Test Scraper', 'web-scraper', {
            maxConcurrent: 2,
            delay: 500
        });
        console.log('Oluşturulan agent:', newAgent);
        console.log('');

        // 3. Agent'ı çalıştır
        console.log('3. Agent çalıştırılıyor...');
        const result = await client.runAgent(newAgent.agentId, {
            url: 'https://example.com',
            selector: 'h1'
        });
        console.log('Çalıştırma sonucu:', result);
        console.log('');

        // 4. Agent durumunu kontrol et
        console.log('4. Agent durumu:');
        const status = await client.getAgentStatus(newAgent.agentId);
        console.log(status);

    } catch (error) {
        console.error('Örnek çalıştırma hatası:', error.message);
    }
}

// Eğer bu dosya doğrudan çalıştırılıyorsa
if (require.main === module) {
    example();
}

module.exports = AgentOSClient;
