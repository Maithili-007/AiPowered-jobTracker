import React, { useState } from "react";
import axios from "axios";
import { useNavigate , Link, NavLink} from 'react-router-dom';

export default function Signup(){

const [form,setForm]=useState({name:"",email:"",password:""});
const [message,setMessage]=useState("");

const handleChange = (e)=>{
setForm({...form,[e.target.name] :e.target.value});
}
const handleSubmit =async(e)=>{
e.preventDefault();

try{
await axios.post("https://aipowered-jobtracker.onrender.com/api/auth/signup",form);
setMessage("Account created! Please login.");
setForm({ name:"", email: "", password: "" });
}
catch(err){
if(err.response && err.response.data && err.response.data.errors){
 setMessage(err.response.data.errors.map(e=>e.msg).join(", "));
}
else{
setMessage("signup failed:"+ (err.response.data.msg? err.response.data.msg : "server error"));
}
}
};
return (
  <div className="container d-flex align-items-center justify-content-center min-vh-100 bg-white">
    <div className="p-4 w-100" style={{ maxWidth: "420px" }}>
      {/* Title */}
      <h2 className="mb-4 text-center fw-bold text-coffee">Sign Up</h2>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        {/* Name */}
        <div className="mb-3">
          <label htmlFor="name" className="form-label text-brown-dark">
            Name <span className="text-brown-dark">*</span>
          </label>
          <input
            id="name"
            name="name"
            type="text"
            className="form-control border-coffee"
            value={form.name}
            onChange={handleChange}
            placeholder="Full Name"
            required
          />
        </div>

        {/* Email */}
        <div className="mb-3">
          <label htmlFor="email" className="form-label text-brown-dark">
            Email Address
          </label>
          <input
            type="email"
            className="form-control border-coffee"
            id="email"
            name="email"
            autoComplete="email"
            value={form.email}
            onChange={handleChange}
            required
            placeholder="Enter your email"
          />
        </div>

        {/* Password */}
        <div className="mb-3">
          <label htmlFor="password" className="form-label text-brown-dark">
            Password
          </label>
          <input
            type="password"
            className="form-control border-coffee"
            id="password"
            name="password"
            autoComplete="new-password"
            value={form.password}
            onChange={handleChange}
            required
            placeholder="Create a password"
          />
        </div>

        {/* Register Button */}
        <button type="submit" className="btn btn-coffee w-100">
          Register
        </button>

        {/* Message */}
        {message && (
          <div className="alert bg-sand mt-3 text-center p-2 border-coffee text-brown-dark">
            {message}
          </div>
        )}
      </form>

      {/* Redirect */}
      <div className="text-center mt-3">
        <small className="text-brown-dark">
          Already have an account?{" "}
          <NavLink to="/login" className="text-coffee text-decoration-none fw-semibold">
            Log in
          </NavLink>
        </small>
      </div>
    </div>
  </div>
);

}