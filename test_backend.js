const axios = require('axios');

async function test() {
  try {
    const loginRes = await axios.post('http://localhost:8000/api/v1/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    const token = loginRes.data.token;
    console.log("Token:", token.substring(0, 10) + "...");
    
    const rulesRes = await axios.get('http://localhost:8000/api/v1/analytics/rules', {
      headers: { 'X-Token': token }
    });
    console.log("Rules available:");
    rulesRes.data.forEach(r => console.log(` - ${r.rule_name}`));

    const projRes = await axios.get('http://localhost:8000/api/v1/projects/', {
      headers: { 'X-Token': token }
    });
    console.log("Projects:", projRes.data.data.length);
    
  } catch (err) {
    console.error("Error:", err.response ? err.response.data : err.message);
  }
}
test();
