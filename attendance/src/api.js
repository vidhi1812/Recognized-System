import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", 
  headers: { "Content-Type": "application/json" },
});


 const registerUser = async (userData) => {
  try {
    const response = await API.post("/api/signup", userData);
    return response.data;
  } catch (error) {
    return error.response?.data || { message: "Something went wrong" };
  }
};


 const loginUser = async (userData) => {
  try {
    const response = await API.post("/api/login", userData);
    return response.data;
  } catch (error) {
    return error.response?.data || { message: "Invalid Credentials" };
  }
};
export {registerUser,loginUser};