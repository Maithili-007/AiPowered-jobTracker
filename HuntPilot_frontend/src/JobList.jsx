import React, { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import AuthContext from './AuthContext';

export default function JobList() {
  const [jobs, setJobs] = useState([]);
  const [errors, setErrors] = useState('');
  const { token } = useContext(AuthContext);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }
    const API_URL = import.meta.env.VITE_API_URL || "https://aipowered-jobtracker.onrender.com";
    axios.get(`${API_URL}/api/jobs`, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        setJobs(res.data);
      })
      .catch(() => {
        setErrors('Failed to load jobs');
      })
  }, [token]);

  // Filtering logic
  const filteredJobs = jobs.filter((job) => {
    // Filter by status
    if (status !== "all" && job.status !== status) return false;

    // Filter by search term (position, company, location)
    if (search.trim()) {
      const term = search.toLowerCase();
      const matchesPosition = job.position && job.position.toLowerCase().includes(term);
      const matchesCompany = job.company && job.company.toLowerCase().includes(term);
      const matchesLocation = job.location && job.location.toLowerCase().includes(term);
      if (!(matchesPosition || matchesCompany || matchesLocation)) {
        return false;
      }
    }

    // Filter by date range
    if (startDate) {
      const start = new Date(startDate);
      const appliedDate = new Date(job.appliedDate);
      if (appliedDate < start) return false;
    }
    if (endDate) {
      const end = new Date(endDate);
      const appliedDate = new Date(job.appliedDate);
      if (appliedDate > end) return false;
    }

    // Passed all filters
    return true;
  });


  return (
    <div className="container mx-auto my-6 px-4">
      {/* 🔍 Filter Section */}
      <div className="card bg-gray-50 border-gray-200 mb-6 p-6">
        <form className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
          {/* Search */}
          <div className="md:col-span-4">
            <input
              type="search"
              className="form-input"
              placeholder="Search jobs, companies, locations..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          {/* Status */}
          <div className="md:col-span-2">
            <label className="form-label">Status</label>
            <select
              className="form-input"
              value={status}
              onChange={e => setStatus(e.target.value)}
            >
              <option value="all">All</option>
              <option value="applied">Applied</option>
              <option value="interviewing">Interviewing</option>
              <option value="offer">Offer</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          {/* Date Range */}
          <div className="md:col-span-2">
            <label className="form-label">From</label>
            <input
              type="date"
              className="form-input"
              value={startDate}
              onChange={e => setStartDate(e.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <label className="form-label">To</label>
            <input
              type="date"
              className="form-input"
              value={endDate}
              onChange={e => setEndDate(e.target.value)}
            />
          </div>

          {/* Clear Button */}
          <div className="md:col-span-2">
            <button
              type="button"
              className="btn-outline w-full"
              onClick={() => {
                setSearch("");
                setStatus("all");
                setStartDate("");
                setEndDate("");
              }}
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      {/* 📋 Job List */}
      <div className="max-w-4xl mx-auto">
        <h2 className="mb-6 text-center text-primary font-bold text-2xl">Your Job Applications</h2>

        {errors && <div className="bg-red-50 border border-red-200 text-red-800 text-center p-4 rounded-lg mb-4">{errors}</div>}

        {jobs.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 text-center p-6 rounded-lg shadow-sm">
            No job applications found.
          </div>
        ) : (
          <div className="space-y-4">
            {filteredJobs.map(job => (
              <div
                key={job._id}
                className="bg-white border border-gray-200 rounded-lg shadow-sm p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-center flex-wrap gap-4">
                  {/* Job Info */}
                  <div className="flex-1">
                    <h5 className="font-semibold text-lg text-gray-900 mb-1">
                      {job.position}
                    </h5>
                    <p className="text-gray-700 mb-2">
                      {job.company} •{' '}
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${{
                        applied: 'bg-blue-100 text-blue-800',
                        interviewing: 'bg-yellow-100 text-yellow-800',
                        offer: 'bg-emerald-100 text-emerald-800',
                        rejected: 'bg-gray-100 text-gray-800'
                      }[job.status] || 'bg-gray-100 text-gray-800'
                        }`}>
                        {job.status}
                      </span>
                    </p>
                  </div>

                  {/* Date + Action */}
                  <div className="text-right">
                    <small className="text-gray-600 block mb-2">
                      {job.appliedDate ? new Date(job.appliedDate).toLocaleDateString() : ''}
                    </small>
                    <Link
                      to={`/jobs/${job._id}`}
                      className="inline-block bg-accent hover:bg-accent-dark text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
