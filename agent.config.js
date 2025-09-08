module.exports = {
    // Genel ayarlar
    general: {
        name: 'Agent OS Project',
        version: '1.0.0',
        description: 'Agent OS entegrasyonu ile proje',
        author: 'User',
        port: process.env.PORT || 3000
    },

    // Agent ayarları
    agents: {
        maxConcurrent: 5,
        defaultTimeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000
    },

    // Agent tipleri
    agentTypes: {
        'web-scraper': {
            enabled: true,
            maxInstances: 3,
            timeout: 60000,
            config: {
                userAgent: 'Agent-OS/1.0',
                delay: 1000,
                maxRetries: 3
            }
        },
        'data-processor': {
            enabled: true,
            maxInstances: 2,
            timeout: 120000,
            config: {
                batchSize: 100,
                memoryLimit: '512MB'
            }
        },
        'api-caller': {
            enabled: true,
            maxInstances: 5,
            timeout: 30000,
            config: {
                retryAttempts: 3,
                retryDelay: 1000
            }
        },
        'generic': {
            enabled: true,
            maxInstances: 10,
            timeout: 60000,
            config: {
                defaultDelay: 500
            }
        }
    },

    // Loglama ayarları
    logging: {
        level: process.env.LOG_LEVEL || 'info',
        file: 'logs/agent-os.log',
        maxSize: '10MB',
        maxFiles: 5
    },

    // API ayarları
    api: {
        baseUrl: process.env.API_BASE_URL || 'http://localhost:3000',
        cors: {
            origin: process.env.CORS_ORIGIN || '*',
            methods: ['GET', 'POST', 'PUT', 'DELETE'],
            allowedHeaders: ['Content-Type', 'Authorization']
        }
    },

    // Güvenlik ayarları
    security: {
        enableAuth: false,
        apiKey: process.env.API_KEY || null,
        rateLimit: {
            windowMs: 15 * 60 * 1000, // 15 dakika
            max: 100 // maksimum 100 istek
        }
    }
};
