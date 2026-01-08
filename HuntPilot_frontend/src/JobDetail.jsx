import React, { useEffect, useState, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
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
    const API_URL = import.meta.env.VITE_API_URL || "https://aipowered-jobtracker.onrender.com";
    axios
      .get(`${API_URL}/api/jobs/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setJob(res.data))
      .catch(() => setError('Failed to load job details'));
  }, [id, token]);

  // Fetch profile match score
  useEffect(() => {
    async function fetchMatch() {
      try {
        const API_URL = import.meta.env.VITE_API_URL || "https://aipowered-jobtracker.onrender.com";
        const res = await fetch(
          `${API_URL}/api/jobs/${id}/match-profile`,
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

  const handleTailorResume = () => {
    // Navigate to resume editor with job ID
    navigate(`/resume-editor/${job._id}`);
  };

  // Delete job
  const handleDeleteClick = async () => {
    if (!window.confirm('Are you sure you want to delete this job?')) return;
    try {
      const API_URL = import.meta.env.VITE_API_URL || "https://aipowered-jobtracker.onrender.com";
      await axios.delete(
        `${API_URL}/api/jobs/${id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      navigate('/jobs'); // redirect after delete
    } catch {
      alert('Failed to delete job.');
    }
  };

  if (error) return <p className="text-red-600">{error}</p>;
  if (!job) return <p>Loading…</p>;

  return (
    <div className="container mx-auto my-8 px-4 max-w-4xl">
      {/* 🔙 Back Link */}
      <Link to="/jobs" className="inline-block mb-6 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors">
        ← Back to Jobs
      </Link>

      {/* 📄 Job Detail Card */}
      <div className="card overflow-hidden">
        {/* Header */}
        <div className="bg-primary text-white p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h4 className="font-bold text-2xl mb-1">{job.position}</h4>
            <small className="text-gray-200">{job.company}</small>
          </div>
          <div className="flex flex-wrap gap-2">
            {/* Styled Buttons */}
            <button
              className="px-4 py-2 bg-primary-dark hover:bg-primary-light text-white font-semibold rounded-lg transition-colors"
              onClick={() => setEditingJob(job)}
            >
              Edit
            </button>
            <button
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
              onClick={handleDeleteClick}
            >
              Delete
            </button>
            <button
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg transition-colors"
              onClick={handleTailorResume}
            >
              Generate Tailored Resume
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-6">
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <strong>Status:</strong>{" "}
                  <span className={`inline-block ml-2 px-3 py-1 rounded-full text-sm font-medium ${{
                    applied: "bg-blue-100 text-blue-800",
                    interviewing: "bg-yellow-100 text-yellow-800",
                    offer: "bg-emerald-100 text-emerald-800",
                    rejected: "bg-gray-100 text-gray-800"
                  }[job.status] || "bg-gray-100 text-gray-800"
                    }`}>
                    {job.status}
                  </span>
                </div>
                <div>
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
                <div className="mb-6">
                  <strong> Notes:</strong>
                  <p className="mt-2 text-gray-600">{job.notes}</p>
                </div>
              )}

              {/* Profile Match Section */}
              {matchResult && (
                <>
                  {matchResult.error ? (
                    <div className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-lg shadow-sm">
                      {matchResult.error}
                    </div>
                  ) : (
                    <div className="card border-accent mb-6">
                      <div className="bg-accent text-white font-bold p-4">
                        Profile Match Score
                      </div>
                      <div className="p-6">
                        {/* Score */}
                        <div className="flex justify-between items-center mb-4">
                          <span>Score</span>
                          <span className="font-bold">{matchResult.score}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-6 mb-6">
                          <div
                            className="bg-accent h-6 rounded-full flex items-center justify-center text-white text-sm font-medium"
                            style={{ width: `${matchResult.score}%` }}
                          >
                            {matchResult.score}%
                          </div>
                        </div>

                        {/* ☕ Matched Keywords */}
                        <div className="mb-4">
                          <h6 className="text-accent font-semibold mb-2">Matched Keywords</h6>
                          {matchResult.matched.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {matchResult.matched.map((kw, i) => (
                                <span
                                  key={i}
                                  className="px-3 py-1 bg-emerald-100 border border-emerald-300 text-emerald-800 rounded-full text-sm"
                                >
                                  {kw}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500">None</p>
                          )}
                        </div>

                        {/* 🫘 Missing Keywords */}
                        <div>
                          <h6 className="text-accent font-semibold mb-2">Missing Keywords</h6>
                          {matchResult.missing.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                              {matchResult.missing.map((kw, i) => (
                                <span
                                  key={i}
                                  className="px-3 py-1 bg-gray-100 border border-gray-300 text-gray-700 rounded-full text-sm"
                                >
                                  {kw}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500">None</p>
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
