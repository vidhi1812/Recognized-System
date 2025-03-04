import React, { useState } from "react";
import "../login/login.css";

const Signup = ({toggleform})=> {
   const[formData, setformData]=useState({
    name:"",
    email:"",
    password:"",
    confirmPassword:""
   });
   const [error, setError] = useState({});

   const handleChange = (e) => {
     setformData({ ...formData, [e.target.name]: e.target.value });
   };
  const handlesubmit = (e) => {
    e.preventDefault();
    let errors = {};

    if(!formData.name) errors.name="name is required";
    if(!formData.email) errors.email="email is required";
    if(!formData.password)errors.password="Password is required";
    if(!formData.confirmPassword) errors.confirmPassword="Confirm password is required";
    if(formData.password !== formData.confirmPassword)
        errors.confirmPassword="Password do not match.";

    if (Object.keys(errors).length === 0) {
      console.log("signup", formData);
      setformData({
        name:"",
        email:"",
        password:"",
        confirmPassword:""
      });
      setError({});
    }
  };

  return (
    <div className="login-cont">
      <div className="log-field1">
        <div className="head">
          {" "}
          <h1>Signup</h1>
        </div>
        {error.general && <p className="error">{error.general}</p>}
        
        <form onSubmit={handlesubmit}>
        <div className="field2">
          <input
           type="text" 
           placeholder=" Praveen kumar"
            name="name" 
           value={formData.name} 
           onChange={handleChange}
           />
           {error.name && <p className="error">{error.name}</p>}
        </div>
        <div className="field2">
          <input
           type="email" 
           placeholder=" xyz@gmail.com"
            name="Email" 
           value={formData.email} 
           onChange={handleChange}
           />
           {error.email && <p className="error">{error.email}</p>}
        </div>
       
        <div className="field2">
          <input 
          type="password" 
          placeholder=" Password" 
          name="Password"
           value={formData.password}
           onChange={handleChange}
           />
           {error.password && <p className="error">{error.password}</p>}
        </div>

        <div className="field2">
          <input 
          type="password" 
          placeholder=" Confirm Password" 
          name=" Confirm Password"
           value={formData.confirmPassword}
           onChange={handleChange}
           />
           {error.confirmPassword && <p className="error">{error.confirmPassword}</p>}
        </div>

        <button className="btn" type="submit">Sign Up

        </button>
        </form>
        <div className="para">
          <p>
            "Already have an account?
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

