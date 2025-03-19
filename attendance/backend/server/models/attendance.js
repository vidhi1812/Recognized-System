import mongoose from 'mongoose';

const attendanceSchema = new mongoose.Schema({
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    userName: { type: String, required: true },  // Store user name for quick lookup
    entryTime: { type: Date, required: true },
    exitTime: { type: Date },  // Nullable - if missing, the user is still present
    status: { type: String, enum: ['Present', 'Absent'], default: 'Present' }
}, { timestamps: true });

const Attendance = mongoose.model('Attendance', attendanceSchema);
export default Attendance;
