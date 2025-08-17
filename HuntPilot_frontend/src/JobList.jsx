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
  return
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
  <>

  <div className="container my-3">
  <form className="row g-3 align-items-end">
    {/* Search Field */}
    <div className="col-12 col-md-4">
      <label htmlFor="searchInput" className="form-label visually-hidden">Search</label>
      <input
        type="search"
        id="searchInput"
        className="form-control rounded-pill"
        placeholder="Search jobs, companies, locations..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
    </div>

    {/* Status Dropdown */}
    <div className="col-6 col-md-2">
      <label htmlFor="statusFilter" className="form-label">Status</label>
      <select
        id="statusFilter"
        className="form-select rounded-pill"
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

    {/* Start Date */}
    <div className="col-6 col-md-2">
      <label htmlFor="startDate" className="form-label">From</label>
      <input
        id="startDate"
        type="date"
        className="form-control rounded-pill"
        value={startDate}
        onChange={e => setStartDate(e.target.value)}
      />
    </div>

    {/* End Date */}
    <div className="col-6 col-md-2">
      <label htmlFor="endDate" className="form-label">To</label>
      <input
        id="endDate"
        type="date"
        className="form-control rounded-pill"
        value={endDate}
        onChange={e => setEndDate(e.target.value)}
      />
    </div>

    {/* Reset/Clear Button */}
    <div className="col-6 col-md-2 d-flex align-items-end">
      <button
        type="button"
        className="btn btn-outline-secondary w-100 rounded-pill"
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

  <div className="container my-4" style={{ maxWidth: '700px' }}>
    <h2 className="mb-4 text-center">Your Job Applications</h2>
    {errors && <p className="text-danger text-center">{errors}</p>}

    {jobs.length === 0 ? (
      <p className="text-center">No job applications found.</p>
    ) : (
      <ul className="list-group">
{filteredJobs.map((job) => (
  <div key={job._id} className="col-12">
    <div className="card border-0 shadow-sm job-hover-transition">
      <div className="card-body d-flex flex-column flex-md-row justify-content-between align-items-center">
        <div>
          <h5 className="card-title mb-1">
            <span className="me-2"><i className="bi bi-briefcase"></i></span>
            {job.position}
          </h5>
          <div className="text-muted mb-0" style={{ fontSize: '1rem' }}>
            {job.company} •{' '}
            <span className={`badge text-capitalize ${{
              applied: 'bg-primary',
              interviewing: 'bg-warning text-dark',
              offer: 'bg-success',
              rejected: 'bg-danger'
            }[job.status] || 'bg-secondary'}`}>
              {job.status}
            </span>
          </div>
        </div>
        <div className="text-end mt-3 mt-md-0">
          <div className="small text-muted">
            <i className="bi bi-calendar"></i>{' '}
            {job.appliedDate ? new Date(job.appliedDate).toLocaleDateString() : ''}
          </div>
          <Link
            to={`/jobs/${job._id}`}
            className="btn btn-outline-secondary btn-sm mt-2"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  </div>
))}
      </ul>
    )}
  </div>
  </>
);
};
