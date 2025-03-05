import express from 'express'
import mongoose from 'mongoose';
import dotenv from "dotenv"
const app = express()
dotenv.config();
const PORT=process.env.PORT || 4000;
const URI=process.env.MongoDBURI



//   connection of MongoDB 

try {
    mongoose.connect(URI);
    console.log("connect to the mongodb");
} catch (error) {
    
}

app.listen(PORT, () => {
  console.log(`Example app listening on port ${PORT}`)
})