import axios from 'axios';

// Fetch daily & monthly present/absent data
export const fetchAttendanceStats = async () => {
    const response = await axios.get('/api/attendance/stats');
    return response.data;
};

// Fetch monthly attendance trends
export const fetchMonthlyTrend = async () => {
    const response = await axios.get('/api/attendance/trend');
    return response.data;
};
