import React, { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "./AuthContext";

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-primary shadow-sm sticky top-0 z-50">
      <div className="container mx-auto max-w-7xl px-4">
        <div className="flex justify-between items-center h-16">
          {/* Brand */}
          <Link className="text-white font-bold text-xl" to="/dashboard">
            HuntPilot
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link className="text-white hover:text-gray-200 transition-colors" to="/dashboard">
              Dashboard
            </Link>
            <Link className="text-white hover:text-gray-200 transition-colors" to="/jobs">
              Jobs
            </Link>
            <Link className="text-white hover:text-gray-200 transition-colors" to="/add-job">
              Add Job
            </Link>
            <Link className="text-white hover:text-gray-200 transition-colors" to="/profile">
              Profile
            </Link>

            {/* User Info & Logout */}
            <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-gray-500">
              <span className="text-gray-200 text-sm">
                <strong>{user?.name || "Guest"}</strong>
              </span>
              <button
                className="bg-primary-dark hover:bg-primary-light text-white px-4 py-2 rounded-lg text-sm transition-colors"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-white p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle navigation"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden pb-4">
            <div className="flex flex-col space-y-2">
              <Link
                className="text-white hover:bg-primary-dark px-3 py-2 rounded transition-colors"
                to="/dashboard"
                onClick={() => setIsMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                className="text-white hover:bg-primary-dark px-3 py-2 rounded transition-colors"
                to="/jobs"
                onClick={() => setIsMenuOpen(false)}
              >
                Jobs
              </Link>
              <Link
                className="text-white hover:bg-primary-dark px-3 py-2 rounded transition-colors"
                to="/add-job"
                onClick={() => setIsMenuOpen(false)}
              >
                Add Job
              </Link>
              <Link
                className="text-white hover:bg-primary-dark px-3 py-2 rounded transition-colors"
                to="/profile"
                onClick={() => setIsMenuOpen(false)}
              >
                Profile
              </Link>
              <div className="pt-2 border-t border-gray-500">
                <span className="text-gray-200 text-sm px-3 block mb-2">
                  Signed in as <strong>{user?.name || "Guest"}</strong>
                </span>
                <button
                  className="bg-primary-dark hover:bg-primary-light text-white px-3 py-2 rounded w-full text-left transition-colors"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
