import React, { useEffect, useState, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import AuthContext from './AuthContext';
import AddJob from './AddJob';

export default function JobDetail() {
  const { id } = useParams();
  const { token } = useContext(AuthContext);
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');
  const [editingJob, setEditingJob]= useState(null);
  const [matchResult, setMatchResult] = useState(null);

  useEffect(() => {
    axios
      .get(`https://aipowered-jobtracker.onrender.com/api/jobs/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setJob(res.data))
      .catch(() => setError('Failed to load job details'));
  }, [id, token]);

  const handleEditClick = (job)=>{
    setEditingJob(job);
  };

  useEffect(() => {
  async function fetchMatch() {
    try {
      const res = await fetch(`/api/jobs/${id}/match-profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      setMatchResult(data);
    } catch (error) {
      console.error('Match fetch error:', error);
      setMatchResult({ error: 'Failed to load match score' });
    }
  }
  
  if (id && token) {
    fetchMatch();
  }
}, [id, token]);

  
  const handleDeleteClick= async (id)=>{
  if (!window.confirm('Are you sure you want to delete this job?')) return;
  try{
   await axios.delete(`https://aipowered-jobtracker.onrender.com /api/jobs/${id}`, {headers: { Authorization: `Bearer ${token}` }, });
   setJob(jobs.filter(job=> job._id !== id));
    setMessage('Job deleted successfully!');
   }
  catch{
   setMessage('Failed to delete job.');
  }
  }
  
  const handleSuccess = ()=>{
    setEditingJob(null);
  };

  if (error) return <p className="text-danger">{error}</p>;
  if (!job) return <p>Loading…</p>;


return (
    <div className="container my-5">
      {/* Back Link */}
      <Link to="/jobs" className="btn btn-outline-secondary mb-4">
        &larr; Back to Jobs
      </Link>

      {/* Job Detail Card */}
      <div className="card shadow-sm">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <div>
            <h4 className="mb-0">{job.position}</h4>
            <small>{job.company}</small>
          </div>
          <div>
            <button
              className="btn btn-light btn-sm me-2"
              onClick={() => setEditingJob(job)}
            >
              Edit
            </button>
          </div>
        </div>

        <div className="card-body">
          {/* Edit Form */}
          {editingJob ? (
            <AddJob
              initialData={editingJob}
              onSuccess={() => {
                setEditingJob(null);
                window.location.reload();
              }}
              onCancel={() => setEditingJob(null)}
            />
          ) : (
            <>
              {/* Status & Date */}
              <p className="mb-1">
                <strong>Status:</strong>{' '}
                <span className="badge bg-info text-dark">{job.status}</span>
              </p>
              <p className="mb-4">
                <strong>Applied:</strong>{' '}
                {new Date(job.appliedDate).toLocaleDateString()}
              </p>

              {/* Location */}
              {job.location && (
                <p className="mb-4">
                  <strong>Location:</strong> {job.location}
                </p>
              )}

              {/* Notes */}
              {job.notes && (
                <div className="mb-4">
                  <strong>Notes:</strong>
                  <p className="mt-2">{job.notes}</p>
                </div>
              )}

              {/* Keywords Extracted */}
              {/* {job.keywords && job.keywords.length > 0 && (
                <div className="mb-4">
                  <strong>Extracted Keywords:</strong>
                  <div className="mt-2">
                    {job.keywords.map((kw, i) => (
                      <span key={i} className="badge bg-secondary me-1 mb-1">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )} */}

              {/* Profile Match Section */}
              {matchResult && matchResult.error ? (
                <div className="alert alert-warning">
                  {matchResult.error}
                </div>
              ) : matchResult && (
                <div className="card border-success mb-4">
                  <div className="card-header bg-success text-white">
                    Profile Match Score
                  </div>
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <span>Score</span>
                      <span className="fw-bold">{matchResult.score}%</span>
                    </div>
                    <div className="progress mb-4" style={{ height: '1.5rem' }}>
                      <div
                        className="progress-bar bg-success"
                        role="progressbar"
                        style={{ width: `${matchResult.score}%` }}
                        aria-valuenow={matchResult.score}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      >
                        {matchResult.score}%
                      </div>
                    </div>
                    <div className="mb-3">
                      <h6 className="text-success">Matched Keywords</h6>
                      {matchResult.matched.length > 0 ? (
                        matchResult.matched.map((kw, i) => (
                          <span key={i} className="badge bg-success me-1 mb-1">
                            {kw}
                          </span>
                        ))
                      ) : (
                        <p className="text-muted">None</p>
                      )}
                    </div>
                    <div>
                      <h6 className="text-danger">Missing Keywords</h6>
                      {matchResult.missing.length > 0 ? (
                        matchResult.missing.map((kw, i) => (
                          <span
                            key={i}
                            className="badge bg-danger me-1 mb-1"
                          >
                            {kw}
                          </span>
                        ))
                      ) : (
                        <p className="text-muted">None</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
