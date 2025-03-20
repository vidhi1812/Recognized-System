import mongoose from "mongoose";

const URI=process.env.MongoDB_URI;
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