import React, { useEffect, useState } from 'react';
import { fetchAttendanceStats, fetchMonthlyTrend } from '../services/attendanceService';
import { listenForAttendanceUpdates } from '../services/socketService';
import { Pie, Bar } from 'react-chartjs-2';

const AdminDashboard = () => {
    const [stats, setStats] = useState({ dailyPresent: 0, dailyAbsent: 0, monthlyPresent: 0, monthlyAbsent: 0 });
    const [trendData, setTrendData] = useState([]);

    const loadStats = async () => {
        const data = await fetchAttendanceStats();
        setStats(data);
    };

    const loadTrend = async () => {
        const data = await fetchMonthlyTrend();
        setTrendData(data);
    };

    useEffect(() => {
        loadStats();
        loadTrend();

        // Listen for real-time updates
        listenForAttendanceUpdates(() => {
            console.log('Attendance data updated, fetching new data...');
            loadStats();
            loadTrend();
        });

    }, []);

    // Pie chart for daily attendance
    const dailyChartData = {
        labels: ['Present', 'Absent'],
        datasets: [{
            data: [stats.dailyPresent, stats.dailyAbsent],
            backgroundColor: ['green', 'red']
        }]
    };

    // Bar chart for monthly trends
    const barChartData = {
        labels: trendData.map(day => `Day ${day._id}`),
        datasets: [{
            label: 'Present Employees',
            data: trendData.map(day => day.count),
            backgroundColor: 'blue'
        }]
    };

    return (
        <div>
            <h2>Admin Dashboard (Live)</h2>

            <div style={{ width: '300px', marginBottom: '20px' }}>
                <h3>Daily Attendance</h3>
                <Pie data={dailyChartData} />
            </div>

            <div style={{ width: '600px' }}>
                <h3>Monthly Attendance Trend</h3>
                <Bar data={barChartData} />
            </div>
        </div>
    );
};

export default AdminDashboard;
