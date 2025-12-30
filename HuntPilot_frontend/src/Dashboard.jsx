import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';

const statusBadgeColors = {
  applied: 'bg-blue-100 text-blue-800',
  interviewing: 'bg-yellow-100 text-yellow-800',
  offer: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-gray-100 text-gray-800'
};

const statusCardColors = {
  applied: 'bg-blue-50 border-blue-200',
  interviewing: 'bg-yellow-50 border-yellow-200',
  offer: 'bg-emerald-50 border-emerald-200',
  rejected: 'bg-gray-50 border-gray-200'
};

export default function Dashboard() {
  const { token, user } = useContext(AuthContext);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState('');
  const [recentJobs, setRecentJobs] = useState([]);

  useEffect(() => {
    console.log("Token in effect:", token);
    if (!token) return;
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
      <h2 className="mb-6 text-center font-bold text-3xl text-primary">
        Welcome {user?.name || 'User'}
      </h2>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 text-center p-4 rounded-lg shadow-sm mb-6">
          {error}
        </div>
      )}

      {/* Status Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {['applied', 'interviewing', 'offer', 'rejected'].map((status) => (
          <div key={status} className="text-center">
            <div className={`card ${statusCardColors[status]} border p-6`}>
              <h6 className="text-sm font-semibold text-gray-700 uppercase mb-2">
                {status}
              </h6>
              <p className="text-3xl font-bold text-gray-900">
                {statusCounts[status] || 0}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Applications */}
      <h3 className="mb-4 font-semibold text-xl text-gray-900">Recent Applications</h3>
      {jobs.length === 0 ? (
        <p className="text-gray-500">You have no job applications yet.</p>
      ) : (
        <div className="space-y-3">
          {recentJobs.map((job) => (
            <div
              key={job._id}
              className="bg-white border border-gray-200 rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start flex-wrap gap-2">
                <h5 className="font-bold text-lg text-primary">{job.position}</h5>
                <small className="text-gray-600">
                  {new Date(job.appliedDate).toLocaleDateString()}
                </small>
              </div>
              <p className="text-gray-700 mt-1">
                {job.company} — {job.location || 'Location not specified'}
              </p>
              <div className="mt-2">
                <span className="text-sm text-gray-600">Status: </span>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${statusBadgeColors[job.status]}`}>
                  {job.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
