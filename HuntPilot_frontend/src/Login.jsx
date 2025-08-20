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
  <div className="container d-flex align-items-center justify-content-center min-vh-100 bg-cream">
    <div className="card shadow p-4 w-100" style={{ maxWidth: "420px" }}>
      {/* Title */}
      <h2 className="mb-4 text-center fw-bold text-coffee">Sign In</h2>

      {/* Form */}
      <form onSubmit={handleSubmit}>
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
            autoComplete="current-password"
            value={form.password}
            onChange={handleChange}
            required
            placeholder="Enter your password"
          />
        </div>

        {/* Login Button */}
        <button type="submit" className="btn btn-coffee w-100">
          Log In
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
          Don&apos;t have an account?{" "}
          <Link
            to="/signup"
            className="text-coffee text-decoration-none fw-semibold"
          >
            Register here
          </Link>
        </small>
      </div>
    </div>
  </div>
);
}

