import express from 'express'
import cors from 'cors';
import dotenv from "dotenv";
dotenv.config();
import cookieParser from 'cookie-parser';
import ConnectMongo from "./Db.js";
import { SignUp, Login } from "../backend/server/controller/authController.js";
import attendanceRoutes from "../backend/server/routes/attendanceRoute.js" 

const app = express()

app.use(cors());
app.use(express.json());
app.use(cookieParser());
const PORT=process.env.PORT || 4000;
ConnectMongo();


app.post('/signup', SignUp);
app.post('/login', Login);



app.use('/attendance', attendanceRoutes);


app.listen(PORT, () => {
  console.log(`Example app listening on port ${PORT}`)
})