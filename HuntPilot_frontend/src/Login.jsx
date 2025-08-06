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
      const res = await axios.post("http://localhost:5000/api/auth/login", form);
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
      <div className="card shadow p-4" style={{ minWidth: "350px", maxWidth: "400px" }}>
        <h2 className="mb-4 text-center">Sign In</h2>
        <form onSubmit={handleSubmit}>
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
              autoComplete="current-password"
              value={form.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>
          <button type="submit" className="btn btn-primary w-100">
            Log In
          </button>
          <div>{message}</div>
        </form>
        <div className="text-center mt-3">
          <small>
            Don't have an account? <Link to="/signup">Register here</Link>
          </small>
        </div>
      </div>
    </div>
  );
}

