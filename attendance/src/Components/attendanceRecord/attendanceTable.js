import React from "react";
import "../attendanceRecord/attendance.css"

const AttendanceTable = () => {
    

    return (
        <div className="attendance-cont">
            <h1 className="atndnchead">Attendance Record</h1>
            <table className="atndncTbl">
                <thead>
                    <tr className="atndncro">
                        <th className="atndncehd">Name</th>
                        <th className="atndncehd">Email</th>
                        <th className="atndncehd">Entry</th>
                        <th className="atndncehd">Exit</th>
                        <th className="atndncehd">Photo</th>
                        <th className="atndncehd">Status</th>
                    </tr>
                </thead>
             
            </table>
        </div>
    );
};

export default AttendanceTable;
