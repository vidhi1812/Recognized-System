import express from 'express'
import dotenv from "dotenv"
dotenv.config();
import ConnectMongo from "./Db.js"
const app = express()

const PORT=process.env.PORT || 4000;


ConnectMongo();

//   connection of MongoDB 



app.listen(PORT, () => {
  console.log(`Example app listening on port ${PORT}`)
})