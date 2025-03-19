import express from 'express'
import cors from 'cors';
import dotenv from "dotenv";
dotenv.config();
import cookieParser from 'cookie-parser';
import ConnectMongo from "./Db.js";
import { Server } from 'socket.io';
import { SignUp, Login } from "../backend/server/controller/authController.js";
import attendanceRoutes from "../backend/server/routes/attendanceRoute.js" 


const app = express()
const server = createServer(app); 
app.use(cors());
app.use(express.json());
app.use(cookieParser());
const PORT=process.env.PORT || 4000;
ConnectMongo();


app.post('/signup', SignUp);
app.post('/login', Login);


app.use('/auth', authRoutes);
app.use('/attendance', attendanceRoutes);

const io = new Server(server, { cors: { origin: '*' } });
io.on("connection", (socket) => {
    console.log("New WebSocket connection:", socket.id);
    socket.on("disconnect", () => console.log("User disconnected"));
});
app.listen(PORT, () => {
  console.log(`Example app listening on port ${PORT}`)
})