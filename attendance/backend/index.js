import express from 'express'
import cors from 'cors';
import dotenv from "dotenv"
import cookieParser from 'cookie-parser';
import ConnectMongo from "./Db.js";
import { SignUp, Login } from './server/controller/authController.js';
dotenv.config();
const app = express()
app.use(cors());
app.use(express.json());
app.use(cookieParser());
const PORT=process.env.PORT || 4000;
ConnectMongo();
// console.log(SignUp)

app.post('/signup', SignUp);
app.post('/login', Login);



app.listen(PORT, () => {
  console.log(`Example app listening on port ${PORT}`)
})