import React,{ useState } from "react";
import "../login/login.css";
import { registerUser } from "../../api";

const Signup = ({ toggleform }) => {
  const [formData, setformData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState({});
  const[message, setMessage]=useState("");
  const handleChange = (e) => {
    setformData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async(e) => {
    e.preventDefault();
   
    let errors = {};

    if (!formData.name) errors.name = "Name is required";
    if (!formData.email) errors.email = "Email is required";
    if (!formData.password) errors.password = "Password is required";
    if (!formData.confirmPassword) errors.confirmPassword = "Confirm password is required";
    if (formData.password !== formData.confirmPassword)
      errors.confirmPassword = "Passwords do not match.";

    if (Object.keys(errors).length === 0) {
      try {
        const response= await registerUser({
          name:"formData.name",
          email:"formData.email",
          password:"formData.password"
        })
        if(response.message){
          setMessage(response.message);
           setformData({name:" ",email:" ", password: " "});
           setError({});
        }
      } catch (err) {
        setError({general:err.message});

      }
    }
    else{
      setError(error);
    }
  };

  return (
    <div className="login-cont">
      <div className="log-field1">
        <div className="head">
          <h1>Signup</h1>
        </div>
        {message && <p className="success" >{message}</p>}
        {error.general && <p className="error">{error.general}</p>}

        <form onSubmit={handleSubmit}>
          <div className="field2">
            <input
              type="text"
              placeholder="Praveen Kumar"
              name="name"
              value={formData.name}
              onChange={handleChange}
            />
            {error.name && <p className="error">{error.name}</p>}
          </div>
          <div className="field2">
            <input
              type="email"
              placeholder="xyz@gmail.com"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
            {error.email && <p className="error">{error.email}</p>}
          </div>

          <div className="field2">
            <input
              type="password"
              placeholder="Password"
              name="password"
              value={formData.password}
              onChange={handleChange}
            />
            {error.password && <p className="error">{error.password}</p>}
          </div>

          <div className="field2">
            <input
              type="password"
              placeholder="Confirm Password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
            {error.confirmPassword && <p className="error">{error.confirmPassword}</p>}
          </div>

          <button className="btn" type="submit">Sign Up</button>
        </form>
        <div className="para">
          <p>
            Already have an account?{" "}
            <span className="forgot" onClick={toggleform}>
              Login
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
