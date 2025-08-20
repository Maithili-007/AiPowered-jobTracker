import React, { useEffect, useState, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import AuthContext from './AuthContext';
//import Navbar from './Navbar';

export default function JobList(){
const [jobs,setJobs]= useState([]);
const[errors,setErrors]= useState('');
const {token} = useContext(AuthContext);
const [search,setSearch]= useState("");
const [status, setStatus] = useState("all");
const [startDate, setStartDate] = useState("");
const [endDate, setEndDate] = useState("");

useEffect(()=>{
if(!token){
  return;
}
axios.get('https://aipowered-jobtracker.onrender.com/api/jobs',{headers:{Authorization:`Bearer ${token}`}})
.then((res)=>{
setJobs(res.data);
})
.catch(()=>{
  setErrors('Failed to load jobs');
})
},[token]);

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
  <div className="container my-4">
    {/* 🔍 Filter Section */}
    <div className="card shadow-sm mb-4 border-0 bg-cream rounded-4">
      <div className="card-body">
        <form className="row g-3 align-items-end">
          {/* Search */}
          <div className="col-12 col-md-4">
            <input
              type="search"
              className="form-control rounded-pill border-coffee"
              placeholder="Search jobs, companies, locations..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>

          {/* Status */}
          <div className="col-6 col-md-2">
            <label className="form-label text-coffee fw-semibold">Status</label>
            <select
              className="form-select rounded-pill border-coffee"
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
          <div className="col-6 col-md-2">
            <label className="form-label text-coffee fw-semibold">From</label>
            <input
              type="date"
              className="form-control rounded-pill border-coffee"
              value={startDate}
              onChange={e => setStartDate(e.target.value)}
            />
          </div>
          <div className="col-6 col-md-2">
            <label className="form-label text-coffee fw-semibold">To</label>
            <input
              type="date"
              className="form-control rounded-pill border-coffee"
              value={endDate}
              onChange={e => setEndDate(e.target.value)}
            />
          </div>

          {/* Clear Button */}
          <div className="col-6 col-md-2">
            <button
              type="button"
              className="btn btn-outline-coffee w-100 rounded-pill"
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
    </div>

    {/* 📋 Job List */}
    <div className="container" style={{ maxWidth: '700px' }}>
      <h2 className="mb-4 text-center text-coffee fw-bold">Your Job Applications</h2>

      {errors && <div className="alert alert-danger text-center">{errors}</div>}

      {jobs.length === 0 ? (
        <div className="alert bg-ice text-center border-0 shadow-sm rounded-3">
          No job applications found.
        </div>
      ) : (
        <div className="list-group">
          {filteredJobs.map(job => (
            <div
              key={job._id}
              className="list-group-item list-group-item-action border-0 shadow-sm mb-3 rounded-4 bg-white-custom"
            >
              <div className="d-flex justify-content-between align-items-center flex-wrap">
                {/* Job Info */}
                <div>
                  <h5 className="mb-1 text-brown-dark fw-semibold">
                    <i className="bi bi-briefcase me-2"></i>{job.position}
                  </h5>
                  <p className="mb-1 text-muted">
                    {job.company} •{' '}
                    <span
                      className={`badge px-3 py-2 rounded-pill bg-${{
                        applied: 'coffee',
                        interviewing: 'latte',
                        offer: 'caramel',
                        rejected: 'dust'
                      }[job.status] || 'secondary'}`}
                    >
                      {job.status}
                    </span>
                  </p>
                </div>

                {/* Date + Action */}
                <div className="text-end">
                  <small className="text-muted d-block mb-2">
                    <i className="bi bi-calendar me-1"></i>
                    {job.appliedDate ? new Date(job.appliedDate).toLocaleDateString() : ''}
                  </small>
                  <Link
                    to={`/jobs/${job._id}`}
                    className="btn btn-outline-coffee btn-sm rounded-pill"
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
