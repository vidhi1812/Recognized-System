import React from 'react'
import "../login/login.css"
const Login = () => {
  return (
    <div className='login-cont'>

      <div className="log-field">
       <div className="head"> <h1>Login </h1></div>
        <div className='field2'>
        <input type="email"   placeholder='xyz@gmail.com' name='Email' />

      </div>
      <div className='field2'>
        <input type="password"   placeholder='Password' name='Email' />
      </div>
      
      <span className='forgot'>Forgot Password?</span>

      <button className='btn'>
        Login 

      </button>
      <div className="para">
        <p>
          Do not have existing account? <span className='forgot'>Sign up</span>
        </p>
      </div>
      </div>
    </div>
  )
}

export default Login
