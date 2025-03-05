import mongoose from "mongoose";
import dotenv from "dotenv"
dotenv.config()
const URI=process.env.MongoDBURI;
const ConnectMongo = async() =>{
    try {
      await mongoose.connect(URI);
        console.log("connect to the mongodb");
    } catch (error) {
        console.log(error);
        process.exit(1);
        
    }

}

export default ConnectMongo;