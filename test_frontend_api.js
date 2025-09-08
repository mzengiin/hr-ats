// Frontend API Test Script
const testLogin = async () => {
    try {
        console.log('Testing API connection...');
        
        const response = await fetch('http://localhost:8001/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: 'demo@example.com',
                password: 'demo123456'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Login successful:', data);
            return true;
        } else {
            const error = await response.text();
            console.log('❌ Login failed:', response.status, error);
            return false;
        }
    } catch (error) {
        console.log('❌ Network error:', error);
        return false;
    }
};

// Test CORS
const testCORS = async () => {
    try {
        console.log('Testing CORS...');
        
        const response = await fetch('http://localhost:8001/api/v1/auth/login', {
            method: 'OPTIONS',
            headers: {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });
        
        console.log('CORS response:', response.status, response.headers.get('Access-Control-Allow-Origin'));
        return response.ok;
    } catch (error) {
        console.log('❌ CORS error:', error);
        return false;
    }
};

// Run tests
console.log('🚀 Starting Frontend API Tests...');
testCORS().then(() => {
    testLogin().then(success => {
        if (success) {
            console.log('🎉 All tests passed! Frontend should work now.');
        } else {
            console.log('💥 Tests failed. Check the issues above.');
        }
    });
});
