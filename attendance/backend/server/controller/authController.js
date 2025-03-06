import Usermodel from '../models/User.js';
import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import createError from "../../server/utils/appError.js";
import dotenv from "dotenv";

dotenv.config();
const  SignUp= async(req,res,next) =>{
try {
    const {name, email,password}=req.body;

    //  check if user exist

     const exist=await Usermodel.findOne({email});
     if(exist)
        return next(createError(400, "User Already Exist"));

    //  Hash Password and save User
    const pass=await bcrypt.hash(password,10);
    const newUser= Usermodel.create({name,email,password:pass});
    
    res.status(200).json({message:"User Created Successfully"});


} catch (error) {
    res.status(500).json({message: error.message});
};
}
const Login = async(req,res,next) =>{

    try {
        const{email, password}= req.body;
        const user=await Usermodel.findOne({email});
        if(!user)
            return next(createError(400,"User not Found"));

        const Match= await bcrypt.compare(password,user.password);
        if(!Match)
            return next(createError(400,"Invaid Credentials"))
        const token=jwt.sign({id:user._id},process.env.JWT_SECRET,{expiresIn:"30min"})
        res.json({message:"Login Successfully",token});
    } catch (error) {
        res.status(500).json({message:error.message});
    };

}
export {SignUp,Login};