import React,{ useRef, useState } from "react"
import Webcam from "react-webcam"
import "../login/login.css";
import "../Signup/Signup.css"
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
  const[image,setImage]=useState(null);
  const[useWebcame,setWebcame]=useState(false);


  const webcame=useRef(null);

  const capturePhoto= () =>{
     if(webcame.current){
  const imageSrc=webcame.current.getScreenshot();
  setImage(imageSrc);
     }
  };

  const handleFileUpload=(e)=>{
    const file=e.target.files[0];
    if(file){
      const render=new FileReader();
      render.onloadend= () =>{
        setImage(render.result);
      }
      render.readAsDataURL(file);
    }
  };
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
    if(!image) errors.image="Image is required!"

    if (Object.keys(errors).length === 0) {
      try {
        const response= await registerUser({
          name:formData.name,
          email:formData.email,
          password:formData.password,
          photo:image
        })
        if(response.message){
          setMessage(response.message);
           setformData({name:" ",email:" ", password: " "});
           setImage(null);
           setError({});
        }
      } catch (err) {
        setError({general:err.message});

      }
    }
    else{
      setError(errors);
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
          {/* Image Upload Options */}
          <div className="field2">
            {image ? (
              <div className="preview-box">
                <img src={image} alt="Uploaded" className="preview-image" />
                <button type="button" onClick={() => setImage(null)} className="btn-small">Change Photo</button>
              </div>
            ) : (
              <>
                <div className="upload-options">
                  {useWebcame ? (
                    <>
                      <Webcam ref={webcame} screenshotFormat="image/jpeg" className="webcam-preview" />
                      <button type="button" onClick={capturePhoto} className="btn-small">Capture</button>
                    </>
                  ) : (
                    <>
                      <input type="file" accept="image/*" onChange={handleFileUpload} style={{ display: "none" }} id="file-upload" />
                      <label htmlFor="file-upload" className="btn-small">Upload File</label>
                    </>
                  )}
                  <button type="button" onClick={() => setWebcame(!useWebcame)} className="btn-small">
                    {useWebcame ? "Use File Upload" : "Use Webcam"}
                  </button>
                </div>
              </>
            )}
          </div>
          {error.image && <p className="error">{error.image}</p>}

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
