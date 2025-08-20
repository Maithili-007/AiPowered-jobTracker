import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';

const statusBadgeColors = {
  applied: 'soft-brown',      // light mocha background
  interviewing: 'coffee',     // warm brown
  offer: 'accent-brown',      // strong coffee accent
  rejected: 'sand'            // soft beige for rejected
};
export default function Dashboard() {
  const { token, user } = useContext(AuthContext);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState('');
  const [recentJobs, setRecentJobs] = useState([]);

  useEffect(() => {
     console.log("Token in effect:", token); 
    if(!token) return;
    axios.get('https://aipowered-jobtracker.onrender.com/api/jobs', {
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
    <div className="p-4">
      {/* Welcome Heading */}
      <h1 className="mb-4 text-center fw-bold text-primary">
        Welcome {user?.name || 'User'}
      </h1>

      {/* Error Alert */}
      {error && (
        <div className="alert text-center bg-soft-brown border-0 shadow-sm rounded-3">
          {error}
        </div>
      )}

      {/* Status Summary Cards */}
      <div className="row g-3 mb-4 justify-content-center">
        {['applied', 'interviewing', 'offer', 'rejected'].map((status) => (
          <div key={status} className="col-6 col-md-3">
            <div
              className={`card text-center shadow-sm border-0 bg-${statusBadgeColors[status]} rounded-3`}
            >
              <div className="card-body">
                <h6 className="card-title text-capitalize fw-semibold text-dark">
                  {status}
                </h6>
                <p className="card-text fs-3 fw-bold text-dark">
                  {statusCounts[status] || 0}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Applications */}
      <h2 className="mb-3 fw-semibold text-dark">Recent Applications</h2>
      {jobs.length === 0 ? (
        <p className="text-muted">You have no job applications yet.</p>
      ) : (
        <div className="list-group shadow-sm rounded-3">
          {recentJobs.map((job) => (
            <div
              key={job._id}
              className="list-group-item list-group-item-action flex-column align-items-start border-0 bg-white-custom"
            >
              <div className="d-flex w-100 justify-content-between">
                <h5 className="mb-1 fw-bold text-primary">{job.position}</h5>
                <small className="text-muted">
                  {new Date(job.appliedDate).toLocaleDateString()}
                </small>
              </div>
              <p className="mb-1 text-secondary">
                {job.company} — {job.location || 'Location not specified'}
              </p>
              <small>
                Status:{' '}
                <span
                  className={`badge bg-soft-brown text-capitalize text-dark px-3 py-2 rounded-pill`}
                >
                  {job.status}
                </span>
              </small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
