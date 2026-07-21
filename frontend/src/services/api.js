// const BASE_URL = "http://localhost:8000";
const BASE_URL = "https://lux-volleyball-backend.onrender.com";

export const fetchTeams = async () => {
    const res = await fetch(`${BASE_URL}/teams`);
if (!res.ok) throw new Error('Failed to fetch teams');
return res.json();
};

export const fetchScoutReport = async (teamId, metricType) => {
// Maps your UI tab names directly to your FastAPI endpoints
const endpointMap = {
                        reception: 'reception-scout',
                        attack: 'attack-scout',
                        service: 'service-scout',
                    // 💡 Future extension addition is now a single line:
// block: 'block-scout'
};

const path = endpointMap[metricType] || 'reception-scout';
const res = await fetch(`${BASE_URL}/teams/${teamId}/${path}`);
if (!res.ok) throw new Error(`Failed to fetch ${metricType} scout report`);
return res.json();
};