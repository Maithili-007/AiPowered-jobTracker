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
    <div className="container d-flex align-items-center justify-content-center min-vh-100 bg-light">
      <div className="card shadow p-4" style={{ minWidth: "350px", maxWidth: "400px" }}>
        <h2 className="mb-4 text-center">Sign Up</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
        <label htmlFor="name" className="form-label">Name<span className="text-danger">*</span></label>
        <input
          id="name"
          name="name"
          type="text"
          className="form-control"
          value={form.name}
          onChange={handleChange}
          placeholder="Full Name"
          required
        />
      </div>
          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              className="form-control"
              id="email"
              name="email"
              autoComplete="email"
              value={form.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              className="form-control"
              id="password"
              name="password"
              autoComplete="new-password"
              value={form.password}
              onChange={handleChange}
              required
              placeholder="Create a password"
            />
          </div>
          <button type="submit" className="btn btn-success w-100">
            Register
          </button>
           <div>{message}</div>
        </form>
        <div className="text-center mt-3">
          <small>
            Already have an account? <NavLink to="/">Log in</NavLink>
          </small>
        </div>
      </div>
    </div>
  );
}