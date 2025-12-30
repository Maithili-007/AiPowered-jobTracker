import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link, NavLink } from 'react-router-dom';

export default function Signup() {

  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  }
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await axios.post("https://aipowered-jobtracker.onrender.com/api/auth/signup", form);
      setMessage("Account created! Please login.");
      setForm({ name: "", email: "", password: "" });
    }
    catch (err) {
      if (err.response && err.response.data && err.response.data.errors) {
        setMessage(err.response.data.errors.map(e => e.msg).join(", "));
      }
      else {
        setMessage("signup failed:" + (err.response.data.msg ? err.response.data.msg : "server error"));
      }
    }
  };
  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <div className="w-full max-w-md">
        {/* Title */}
        <h2 className="mb-6 text-center font-bold text-3xl text-primary">Sign Up</h2>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md">
          {/* Name */}
          <div className="mb-4">
            <label htmlFor="name" className="form-label">
              Name <span className="text-red-500">*</span>
            </label>
            <input
              id="name"
              name="name"
              type="text"
              className="form-input"
              value={form.name}
              onChange={handleChange}
              placeholder="Full Name"
              required
            />
          </div>

          {/* Email */}
          <div className="mb-4">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              className="form-input"
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
          <div className="mb-6">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              className="form-input"
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
          <button type="submit" className="btn-primary w-full">
            Register
          </button>

          {/* Message */}
          {message && (
            <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-center text-amber-800">
              {message}
            </div>
          )}
        </form>

        {/* Redirect */}
        <div className="text-center mt-4">
          <small className="text-gray-600">
            Already have an account?{" "}
            <NavLink to="/login" className="text-accent hover:text-accent-dark font-semibold transition-colors">
              Log in
            </NavLink>
          </small>
        </div>
      </div>
    </div>
  );

}