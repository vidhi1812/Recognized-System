import Attendance from "../models/attendanceModel.js";

export const markEntry = async (req, res) => {
    const { userId } = req.body;

    try {
        const existingRecord = await Attendance.findOne({ userId, exitTime: null });
        if (existingRecord) return res.status(400).json({ message: "User is already checked in." });

        const newEntry = new Attendance({ userId, entryTime: new Date(), status: "Present" });
        await newEntry.save();
        res.json({ message: "Entry marked", entry: newEntry });

    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
};

export const markExit = async (req, res) => {
    const { userId } = req.body;

    try {
        const record = await Attendance.findOne({ userId, exitTime: null });
        if (!record) return res.status(400).json({ message: "No active entry found" });

        record.exitTime = new Date();
        record.status = "Absent";
        await record.save();

        res.json({ message: "Exit marked", exit: record });

    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
};

export const getAllAttendance = async (req, res) => {
    try {
        const records = await Attendance.find().populate("userId", "name email profilePic");
        res.json(records);
    } catch (error) {
        res.status(500).json({ message: "Server Error" });
    }
};
