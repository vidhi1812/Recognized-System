import React from 'react'
// import {useNavigate} from "react-router-dom"
import "../Nav/Nav.css"
const Nav = () => {
  // const navigate=useNavigate();


  
  
  return (
    <div className='Nav'>
     <div className="nav-left">
      Hii
     </div>
     <div className="nav-center">
      <ul className='list'>
        <li className='list1'>Home</li>
        <li className='list1'>About</li>
        <li className='list1'>Members</li>
        <li className='list1'>Contact</li>
      </ul>
     </div>
   <div className='nav-right'>
    <button className='log-btn' >Logout</button>
   </div>
   
      
    </div>
  )
}

export default Nav;
