import Attendance from '../models/attendance.js';

// Mark user entry (Check-in)
export const markEntry = async (req, res) => {
    const { userId, userName } = req.body;

    try {
        const existingRecord = await Attendance.findOne({ userId, exitTime: null });

        if (existingRecord) {
            return res.status(400).json({ message: 'User is already checked in.' });
        }

        const newEntry = new Attendance({
            userId,
            userName,
            entryTime: new Date(),
            status: 'Present'
        });

        await newEntry.save();
        res.status(201).json({ message: 'Entry marked successfully', entry: newEntry });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Server Error' });
    }
};

// Mark user exit (Check-out)
export const markExit = async (req, res) => {
    const { userId } = req.body;

    try {
        const attendanceRecord = await Attendance.findOne({ userId, exitTime: null });

        if (!attendanceRecord) {
            return res.status(400).json({ message: 'No active entry found for this user.' });
        }

        attendanceRecord.exitTime = new Date();
        attendanceRecord.status = 'Absent';
        await attendanceRecord.save();

        res.status(200).json({ message: 'Exit marked successfully', exit: attendanceRecord });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Server Error' });
    }
};

// Fetch all attendance records
export const getAllAttendance = async (req, res) => {
    try {
        const attendanceRecords = await Attendance.find().sort({ entryTime: -1 });
        res.status(200).json(attendanceRecords);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Server Error' });
    }
};
