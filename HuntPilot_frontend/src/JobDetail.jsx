import React, { useEffect, useState, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom'; // useNavigate for v6
import axios from 'axios';
import AuthContext from './AuthContext';
import AddJob from './AddJob';

export default function JobDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token } = useContext(AuthContext);
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');
  const [editingJob, setEditingJob] = useState(null);
  const [matchResult, setMatchResult] = useState(null);

  // Fetch job details
  useEffect(() => {
    axios
      .get(`https://aipowered-jobtracker.onrender.com/api/jobs/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setJob(res.data))
      .catch(() => setError('Failed to load job details'));
  }, [id, token]);

  // Fetch profile match score
  useEffect(() => {
    async function fetchMatch() {
      try {
        const res = await fetch(
          `https://aipowered-jobtracker.onrender.com/api/jobs/${id}/match-profile`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          }
        );

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

  // Delete job
  const handleDeleteClick = async () => {
    if (!window.confirm('Are you sure you want to delete this job?')) return;
    try {
      await axios.delete(
        `https://aipowered-jobtracker.onrender.com/api/jobs/${id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      navigate('/jobs'); // redirect after delete
    } catch {
      alert('Failed to delete job.');
    }
  };

  if (error) return <p className="text-danger">{error}</p>;
  if (!job) return <p>Loading…</p>;

return (
  <div className="container my-5">
    {/* 🔙 Back Link */}
    <Link to="/jobs" className="btn btn-outline-brown btn-coffee mb-4 rounded-pill shadow-sm">
      ← Back to Jobs
    </Link>

    {/* 📄 Job Detail Card */}
    <div className="card shadow-sm border-0 rounded-4 overflow-hidden">
      {/* Header */}
      <div className="card-header bg-cream text-dark d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center">
        <div className="mb-2 mb-md-0">
          <h4 className="mb-1 fw-bold">{job.position}</h4>
          <small className="text-light">{job.company}</small>
        </div>
        <div className="d-flex gap-2">
          {/* Styled Buttons */}
          <button
            className="btn btn-sm btn-outline-light btn-coffee fw-semibold px-3 rounded-pill d-flex align-items-center gap-1"
            onClick={() => setEditingJob(job)}
          >
             Edit
          </button>
          <button
            className="btn btn-sm btn-outline-light btn-coffee fw-semibold px-3 rounded-pill d-flex align-items-center gap-1"
            onClick={handleDeleteClick}
          >
             Delete
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="card-body">
        {/* ✍️ Edit Mode */}
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
            <div className="row mb-4">
              <div className="col-12 col-md-6 mb-2">
                <strong>Status:</strong>{" "}
                <span className={`badge bg-${{
                  applied: "caramel",
                  interviewing: "caramel",
                  offer: "caramel",
                  rejected: "caramel"
                }[job.status] || "secondary"} text-dark px-3 py-2 rounded-pill`}>
                  {job.status}
                </span>
              </div>
              <div className="col-12 col-md-6">
                <strong>Applied:</strong>{" "}
                {new Date(job.appliedDate).toLocaleDateString()}
              </div>
            </div>

            {/* Location */}
            {job.location && (
              <p className="mb-4">
                <strong> Location:</strong> {job.location}
              </p>
            )}

            {/* Notes */}
            {job.notes && (
              <div className="mb-4">
                <strong> Notes:</strong>
                <p className="mt-2 text-muted">{job.notes}</p>
              </div>
            )}

            {/* Profile Match Section */}
            {matchResult && (
              <>
                {matchResult.error ? (
                  <div className="alert alert-warning rounded-3 shadow-sm">
                    {matchResult.error}
                  </div>
                ) : (
                  <div className="card border-coffee mb-4 shadow-sm rounded-3">
                    <div className="card-header bg-cream text-dark fw-bold">
                      Profile Match Score
                    </div>
                    <div className="card-body">
                      {/* Score */}
                      <div className="d-flex justify-content-between align-items-center mb-3">
                        <span>Score</span>
                        <span className="fw-bold">{matchResult.score}%</span>
                      </div>
                      <div
                        className="progress mb-4 rounded-pill"
                        style={{ height: "1.5rem" }}
                      >
                        <div
                          className="progress-bar bg-coffee"
                          role="progressbar"
                          style={{ width: `${matchResult.score}%` }}
                          aria-valuenow={matchResult.score}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        >
                          {matchResult.score}%
                        </div>
                      </div>

                      {/* ☕ Matched Keywords */}
                      <div className="mb-3">
                        <h6 className="text-coffee">Matched Keywords</h6>
                        {matchResult.matched.length > 0 ? (
                          matchResult.matched.map((kw, i) => (
                            <span
                              key={i}
                              className="badge bg-mocha border-coffee text-dark me-1 mb-1"
                            >
                              {kw}
                            </span>
                          ))
                        ) : (
                          <p className="text-muted">None</p>
                        )}
                      </div>

                      {/* 🫘 Missing Keywords */}
                      <div>
                        <h6 className="text-coffee">Missing Keywords</h6>
                        {matchResult.missing.length > 0 ? (
                          matchResult.missing.map((kw, i) => (
                            <span
                              key={i}
                              className="badge bg-soft-white border-coffee text-dark me-1 mb-1"
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
          </>
        )}
      </div>
    </div>
  </div>
);
}



