import React, { useState, useContext } from "react";
import axios from "axios";
import AuthContext from "./AuthContext";
import { useNavigate , Link} from "react-router-dom";

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
  <div className="container d-flex align-items-center justify-content-center min-vh-100 bg-light">
    <div className="card shadow p-4 w-100" style={{ maxWidth: "420px" }}>
      {/* Title */}
      <h2 className="mb-4 text-center fw-bold text-primary">Sign In</h2>

      {/* Form */}
      <form onSubmit={handleSubmit}>
        {/* Email */}
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

        {/* Password */}
        <div className="mb-3">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            type="password"
            className="form-control"
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
        <button type="submit" className="btn btn-primary w-100">
          Log In
        </button>

        {/* Message */}
        {message && (
          <div className="alert alert-info mt-3 text-center p-2">
            {message}
          </div>
        )}
      </form>

      {/* Redirect */}
      <div className="text-center mt-3">
        <small>
          Don&apos;t have an account?{" "}
          <Link to="/signup" className="text-decoration-none">
            Register here
          </Link>
        </small>
      </div>
    </div>
  </div>
);

}

