import express from "express";
import { markEntry, markExit, getAllAttendance } from "../controllers/attendanceController.js";

const router = express.Router();
router.post("/entry", markEntry);
router.post("/exit", markExit);
router.get("/all", getAllAttendance);

export default router;
