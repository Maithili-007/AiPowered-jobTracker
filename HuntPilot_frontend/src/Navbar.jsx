import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "./AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

return (
  <nav className="navbar navbar-expand-lg shadow-sm sticky-top bg-coffee">
  <div className="container">
    {/* Brand */}
    <Link className="navbar-brand fw-bold text-white" to="/dashboard">
      HuntPilot
    </Link>

    {/* Toggle button */}
    <button
      className="navbar-toggler border-0"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarNav"
      aria-controls="navbarNav"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span className="navbar-toggler-icon"></span>
    </button>

    {/* Collapsible Menu */}
    <div className="collapse navbar-collapse" id="navbarNav">
      <ul className="navbar-nav me-auto mb-2 mb-lg-0">
        <li className="nav-item">
          <Link className="nav-link text-white" to="/dashboard">
            Dashboard
          </Link>
        </li>
        <li className="nav-item">
          <Link className="nav-link text-white" to="/jobs">
            Jobs
          </Link>
        </li>
        <li className="nav-item">
          <Link className="nav-link text-white" to="/add-job">
            Add Job
          </Link>
        </li>
        <li className="nav-item">
          <Link className="nav-link text-white" to="/profile">
            Profile
          </Link>
        </li>
      </ul>

      {/* Right side */}
      <ul className="navbar-nav ms-auto align-items-lg-center">
        <li className="nav-item me-2">
          <span className="navbar-text text-dark small">
            Signed in as <strong>{user?.name || "Guest"}</strong>
          </span>
        </li>
        <li className="nav-item">
          <button
            className="btn bg-coffee btn-sm"
            onClick={handleLogout}
          >
            Logout
          </button>
        </li>
      </ul>
    </div>
  </div>
</nav>
);
}
