import React, { useState } from "react";
import "../login/login.css";
const Login = ({toggleform}) => {
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState({})
  
  

  const handlesubmit = (e) => {
    e.preventDefault();
    let errors = {};

    if (!email && !password) {
      errors.general = "Please enter required fields.";
    } else {
      if (!email) {
        errors.email = "Please enter your email.";
      }
      if (!password) {
        errors.password = "Please enter valid password.";
      }
    }
    setError(errors);

    if (Object.keys(errors).length === 0) {
      console.log("LOGIN", { email, password });
      setEmail("");
      setPassword("");
      setError({});
    }
  };

  return (
    <div className="login-cont">
      <div className="log-field">
        <div className="head">
          {" "}
          <h1>Login</h1>
        </div>
        {error.general && <p className="error">{error.general}</p>}
        
        <form onSubmit={handlesubmit}>
        <div className="field2">
          <input
           type="email" 
           placeholder="xyz@gmail.com"
            name="Email" 
           value={email} 
           onChange={(e) => setEmail(e.target.value)}
           />
           {error.email && <p className="error">{error.email}</p>}
        </div>
       
        <div className="field2">
          <input 
          type="password" 
          placeholder="Password" 
          name="Password"
           value={password}
           onChange={(e) => setPassword(e.target.value)}
           />
           {error.password && <p className="error">{error.password}</p>}
        </div>

      <span className="forgot">Forgot Password?</span>

        <button className="btn" type="submit">Login

        </button>
        </form>
        <div className="para">
          <p>
            "Do not have an account?"
            <span className="forgot" onClick={toggleform}>
              Signup
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
