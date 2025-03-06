import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:4001", // Change this if using a different backend URL
  headers: { "Content-Type": "application/json" },
});

// Register (SignUp)
 const registerUser = async (userData) => {
  try {
    const response = await API.post("/signup", userData);
    return response.data;
  } catch (error) {
    return error.response?.data || { message: "Something went wrong" };
  }
};

// Login
 const loginUser = async (userData) => {
  try {
    const response = await API.post("/login", userData);
    return response.data;
  } catch (error) {
    return error.response?.data || { message: "Invalid Credentials" };
  }
};
export {registerUser,loginUser};