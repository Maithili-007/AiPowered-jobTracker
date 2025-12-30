import React, { useState, useContext } from "react";
import axios from "axios";
import AuthContext from "./AuthContext";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await axios.post("https://aipowered-jobtracker.onrender.com/api/auth/login", form);
      login(res.data);
      navigate("/");
    } catch (err) {
      if (err.response && err.response.data && err.response.data.errors) {
        setMessage(err.response.data.errors.map(e => e.msg).join(", "));
      } else {
        setMessage("Login failed: " + (err.response ? err.response.data.message : "Server error"));
      }
    }
  };
  return (
    <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
      <div className="w-full max-w-md">
        {/* Title */}
        <h2 className="mb-6 text-center font-bold text-3xl text-primary">Sign In</h2>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md">
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
              autoComplete="current-password"
              value={form.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {/* Login Button */}
          <button type="submit" className="btn-primary w-full">
            Log In
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
            Don&apos;t have an account?{" "}
            <Link
              to="/signup"
              className="text-accent hover:text-accent-dark font-semibold transition-colors"
            >
              Register here
            </Link>
          </small>
        </div>
      </div>
    </div>
  );
}
