import express from 'express';
import { markEntry, markExit, getAllAttendance } from '../controller/attendanceController.js';

const router = express.Router();

// Routes for marking attendance
router.post('/entry', markEntry);
router.post('/exit', markExit);
router.get('/all', getAllAttendance);

export default router;
