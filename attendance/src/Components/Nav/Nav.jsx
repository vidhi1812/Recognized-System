import React from 'react'
import "../Nav/Nav.css"
const Nav = () => {
  

  
  
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
