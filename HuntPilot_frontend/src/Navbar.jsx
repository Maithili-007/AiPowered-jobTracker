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
  <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm sticky-top">
    <div className="container">
      {/* Brand */}
      <Link className="navbar-brand fw-bold" to="/dashboard">
        HuntPilot
      </Link>

      {/* Mobile Toggle Button */}
      <button
        className="navbar-toggler"
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
        {/* Left side nav links */}
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          <li className="nav-item">
            <Link className="nav-link" to="/dashboard">Dashboard</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/jobs">Jobs</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/add-job">Add Job</Link>
          </li>
          <li className="nav-item">
            <Link className="nav-link" to="/profile">Profile</Link>
          </li>
        </ul>

        {/* Right side user info + logout */}
        <ul className="navbar-nav ms-auto align-items-lg-center">
          <li className="nav-item d-lg-flex align-items-center me-2">
            <span className="navbar-text text-white small">
              Signed in as <strong>{user?.name || "Guest"}</strong>
            </span>
          </li>
          <li className="nav-item">
            <button 
              className="btn btn-outline-light btn-sm w-100 w-lg-auto" 
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
