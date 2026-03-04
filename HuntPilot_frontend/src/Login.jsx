import React, { useState, useContext } from "react";
import nodeApi from "./api/clientNode";
import AuthContext from "./AuthContext";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSubmit = async e => {
    e.preventDefault();
    setMessage("");
    setIsSubmitting(true);
    try {
      const res = await nodeApi.post('/api/auth/login', form);
      login(res.data);
      navigate("/");
    } catch (err) {
      if (err.response && err.response.data && err.response.data.errors) {
        setMessage(err.response.data.errors.map(e => e.msg).join(", "));
      } else {
        setMessage("Login failed: " + (err.response ? err.response.data.message : "Server error"));
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoLogin = async () => {
    setMessage("");
    setIsDemoLoading(true);
    try {
      const res = await nodeApi.post('/api/auth/demo-login');
      login(res.data);
      navigate("/");
    } catch (err) {
      setMessage("Demo login failed: " + (err.response ? err.response.data.message : "Server error"));
    } finally {
      setIsDemoLoading(false);
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
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting || isDemoLoading}>
            {isSubmitting ? "Logging in..." : "Log In"}
          </button>

          <button
            type="button"
            onClick={handleDemoLogin}
            className="mt-3 w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 font-semibold text-gray-700 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-70"
            disabled={isSubmitting || isDemoLoading}
          >
            {isDemoLoading ? "Signing into demo..." : "Try Demo"}
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
