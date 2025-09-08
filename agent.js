const express = require('express');
const axios = require('axios');
require('dotenv').config();

class AgentOS {
    constructor() {
        this.app = express();
        this.port = process.env.PORT || 3000;
        this.agents = new Map();
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.static('public'));
    }

    setupRoutes() {
        // Ana sayfa
        this.app.get('/', (req, res) => {
            res.json({
                message: 'Agent OS API çalışıyor',
                version: '1.0.0',
                agents: Array.from(this.agents.keys())
            });
        });

        // Agent oluşturma
        this.app.post('/agents', (req, res) => {
            const { name, type, config } = req.body;
            const agentId = this.createAgent(name, type, config);
            res.json({ agentId, message: 'Agent oluşturuldu' });
        });

        // Agent listesi
        this.app.get('/agents', (req, res) => {
            res.json(Array.from(this.agents.entries()).map(([id, agent]) => ({
                id,
                name: agent.name,
                type: agent.type,
                status: agent.status
            })));
        });

        // Agent çalıştırma
        this.app.post('/agents/:id/run', (req, res) => {
            const { id } = req.params;
            const { task } = req.body;
            
            if (!this.agents.has(id)) {
                return res.status(404).json({ error: 'Agent bulunamadı' });
            }

            this.runAgent(id, task)
                .then(result => res.json({ result }))
                .catch(error => res.status(500).json({ error: error.message }));
        });

        // Agent durumu
        this.app.get('/agents/:id/status', (req, res) => {
            const { id } = req.params;
            const agent = this.agents.get(id);
            
            if (!agent) {
                return res.status(404).json({ error: 'Agent bulunamadı' });
            }

            res.json({
                id,
                name: agent.name,
                type: agent.type,
                status: agent.status,
                lastRun: agent.lastRun
            });
        });
    }

    createAgent(name, type, config = {}) {
        const agentId = `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const agent = {
            id: agentId,
            name,
            type,
            config,
            status: 'idle',
            lastRun: null,
            createdAt: new Date()
        };

        this.agents.set(agentId, agent);
        console.log(`Agent oluşturuldu: ${name} (${agentId})`);
        return agentId;
    }

    async runAgent(agentId, task) {
        const agent = this.agents.get(agentId);
        if (!agent) {
            throw new Error('Agent bulunamadı');
        }

        agent.status = 'running';
        agent.lastRun = new Date();

        try {
            let result;
            
            switch (agent.type) {
                case 'web-scraper':
                    result = await this.runWebScraperAgent(agent, task);
                    break;
                case 'data-processor':
                    result = await this.runDataProcessorAgent(agent, task);
                    break;
                case 'api-caller':
                    result = await this.runApiCallerAgent(agent, task);
                    break;
                default:
                    result = await this.runGenericAgent(agent, task);
            }

            agent.status = 'completed';
            return result;
        } catch (error) {
            agent.status = 'error';
            throw error;
        }
    }

    async runWebScraperAgent(agent, task) {
        // Web scraping işlemi simülasyonu
        await new Promise(resolve => setTimeout(resolve, 1000));
        return {
            type: 'web-scraper',
            task,
            result: `Web scraping tamamlandı: ${task.url || 'URL belirtilmedi'}`,
            timestamp: new Date()
        };
    }

    async runDataProcessorAgent(agent, task) {
        // Veri işleme simülasyonu
        await new Promise(resolve => setTimeout(resolve, 1500));
        return {
            type: 'data-processor',
            task,
            result: `Veri işleme tamamlandı: ${task.dataType || 'Veri tipi belirtilmedi'}`,
            timestamp: new Date()
        };
    }

    async runApiCallerAgent(agent, task) {
        // API çağrısı simülasyonu
        await new Promise(resolve => setTimeout(resolve, 800));
        return {
            type: 'api-caller',
            task,
            result: `API çağrısı tamamlandı: ${task.endpoint || 'Endpoint belirtilmedi'}`,
            timestamp: new Date()
        };
    }

    async runGenericAgent(agent, task) {
        // Genel agent işlemi
        await new Promise(resolve => setTimeout(resolve, 500));
        return {
            type: 'generic',
            task,
            result: `Görev tamamlandı: ${task.description || 'Açıklama belirtilmedi'}`,
            timestamp: new Date()
        };
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`Agent OS sunucusu http://localhost:${this.port} adresinde çalışıyor`);
            console.log('Mevcut endpointler:');
            console.log('  GET  / - Ana sayfa');
            console.log('  POST /agents - Yeni agent oluştur');
            console.log('  GET  /agents - Agent listesi');
            console.log('  POST /agents/:id/run - Agent çalıştır');
            console.log('  GET  /agents/:id/status - Agent durumu');
        });
    }
}

// Eğer bu dosya doğrudan çalıştırılıyorsa
if (require.main === module) {
    const agentOS = new AgentOS();
    agentOS.start();
}

module.exports = AgentOS;
