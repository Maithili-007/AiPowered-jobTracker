import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';

const statusBadgeColors = {//object
  applied: 'primary',     
  interviewing: 'warning', 
  offer: 'success',      
  rejected: 'danger'     
};
export default function Dashboard() {
  const { token, user } = useContext(AuthContext);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState('');
  const [recentJobs, setRecentJobs] = useState([]);

  useEffect(() => {
     console.log("Token in effect:", token); 
    if(!token) return;
    axios.get('http://localhost:5000/api/jobs', {
      headers: { Authorization: `Bearer ${token}` }
    })
     .then((res) => {
        const sorted = res.data.sort(
          (a, b) => new Date(b.appliedDate) - new Date(a.appliedDate)
        );
        const recent = sorted.slice(0, 3);
        setRecentJobs(recent);
        setJobs(sorted);
      })
    .catch(err => {
      console.error(err);
      setError('Failed to load jobs');
    });
  }, [token]);

  const statusCounts = jobs.reduce((acc, job) => {
    acc[job.status] = (acc[job.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <>
    <div className="container my-4">
      <h1 className="mb-4 text-center">Welcome {user?.name || 'User'} to Your Dashboard</h1>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Status Summary Cards */}
      <div className="row mb-4 justify-content-center">
        {['applied', 'interviewing', 'offer', 'rejected'].map(status => (
          <div key={status} className="col-2 col-md-2 mb-0">
            <div className={`card text-center text-white bg-${statusBadgeColors[status]}`}>
              <div className="card-body">
                <h5 className="card-title text-capitalize">{status}</h5>
                <p className="card-text fs-3">{statusCounts[status] || 0}</p>
              </div>
            </div>
            
          </div>
        ))}
      </div>

      <h2 className="mb-3">Recent Applications</h2>
      {jobs.length === 0 ? (
        <p>You have no job applications yet.</p>
      ) : (
        <div className="list-group">
          {recentJobs.map(job => (// returning a multi-line JSX block
            <div key={job._id} className="list-group-item list-group-item-action flex-column align-items-start">
              <div className="d-flex w-100 justify-content-between">
                <h5 className="mb-1">{job.position}</h5>
                <small>{new Date(job.appliedDate).toLocaleDateString()}</small>
              </div>
              <p className="mb-1">{job.company} — {job.location || 'Location not specified'}</p>
              <small>
                Status: <span className={`badge bg-${statusBadgeColors[job.status]} text-capitalize`}>{job.status}</span>
              </small>
            </div>
          ))}
        </div>
      )}
    </div>
    </>
  );
}
