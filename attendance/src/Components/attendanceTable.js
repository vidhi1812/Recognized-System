import React, { useState, useEffect } from "react";
import axios from "axios";

const AttendanceTable = () => {
    const [attendance, setAttendance] = useState([]);

    useEffect(() => {
        fetchAttendance();
    }, []);

    const fetchAttendance = async () => {
        try {
            const response = await axios.get("http://localhost:4000/attendance/all"); // ✅ Fixed API Call
            setAttendance(response.data);
        } catch (error) {
            console.error("Error during attendance fetching:", error);
        }
    };

    return (
        <div className="attendance-page p-4">
            <h1 className="attendance-head text-2xl font-bold mb-4">Attendance Record</h1>
            <table className="attendanceTable w-full border-collapse border border-gray-300">
                <thead>
                    <tr className="tableRow bg-gray-200">
                        <th className="tablehead p-2 border">Name</th>
                        <th className="tablehead p-2 border">Email</th>
                        <th className="tablehead p-2 border">Entry</th>
                        <th className="tablehead p-2 border">Exit</th>
                        <th className="tablehead p-2 border">Photo</th>
                        <th className="tablehead p-2 border">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {attendance.map((record) => (
                        <tr key={record._id} className="border">
                            <td className="border p-2">{record.userId?.name || "Unknown"}</td>
                            <td className="border p-2">{record.userId?.email || "No Email"}</td>
                            <td className="border p-2">
                                {record.entryTime ? new Date(record.entryTime).toLocaleString() : "No Entry"}
                            </td>
                            <td className="border p-2">
                                {record.exitTime ? new Date(record.exitTime).toLocaleString() : "Still Present"}
                            </td>
                            <td className="border p-2">
                                <img
                                    src={record.userId?.profilePic || "https://via.placeholder.com/50"}
                                    alt="User"
                                    className="w-12 h-12 rounded-full"
                                />
                            </td>
                            <td
                                className={`border p-2 ${
                                    record.status === "Present" ? "text-green-500" : "text-red-500"
                                }`}
                            >
                                {record.status}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AttendanceTable;
