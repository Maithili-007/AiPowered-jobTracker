import React, { useState, useContext, useEffect } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';
import { useNavigate, NavLink } from 'react-router-dom';

export default function AddJob({ initialData, onSuccess, onCancel }) {
  const [form, setForm] = useState({ position: '', company: '', status: 'applied', location: '', notes: '', ...initialData || {} });
  const [message, setMessage] = useState('');
  const { token } = useContext(AuthContext);
  const navigate = useNavigate();

  const [description, setDescription] = useState('');
  const [suggestedKeywords, setSuggestedKeywords] = useState([]);
  const [selectedKeywords, setSelectedKeywords] = useState([]);
  const [loadingKeywords, setLoadingKeywords] = useState(false);
  const [keywordError, setKeywordError] = useState('');


  useEffect(() => {
    setForm({
      position: "",
      company: "",
      status: "applied",
      location: "",
      notes: "",
      ...(initialData || {})
    });
    setDescription(initialData?.description || '');
    setSelectedKeywords(initialData?.keywords || []);
  }, [initialData]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });//curly brackets because you're creating a new object.
  }

  useEffect(() => {
    if (!description) {
      setSuggestedKeywords([]);//dont do anything if no description
      return;
    }
    const timeout = setTimeout(async () => {
      setLoadingKeywords(true);//we are now starting to extract keywords
      setKeywordError('');
      try {
        const ANALYSIS_URL = import.meta.env.VITE_ANALYSIS_API_URL || "https://aipowered-jobtracker-1.onrender.com";
        const resp = await fetch(`${ANALYSIS_URL}/extract-keywords`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ description }),
        });
        if (!resp.ok) throw new Error(`Status ${resp.status}`);
        const { keywords } = await resp.json();
        setSuggestedKeywords(keywords);
        if (selectedKeywords.length === 0) {
          //setSelectedKeywords(keywords.slice(0, 5));
          setSelectedKeywords(keywords);
        }
      } catch (e) {
        console.error('Fetch error:', e.message);
        setKeywordError('Failed to extract keywords');
      } finally {
        setLoadingKeywords(false);
      }
    }, 500);
    return () => clearTimeout(timeout);//cancel the previous timeout before setting a new one
  }, [description, token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const isEdit = !!(initialData && initialData._id);
    const API_URL = import.meta.env.VITE_API_URL || "https://aipowered-jobtracker.onrender.com";
    const url = isEdit ? `${API_URL}/api/jobs/${initialData._id}` : `${API_URL}/api/jobs`;
    const method = isEdit ? "put" : "post";

    const payload = {
      ...form,
      description,
      keywords: selectedKeywords
    };


    try {
      const res = await axios[method](url, payload, { headers: { Authorization: `Bearer ${token}` } });
      setMessage(isEdit ? "Job updated!" : "Job added!");
      if (onSuccess) onSuccess(res.data, isEdit);
      setForm({ position: '', company: '', status: 'applied', location: '', notes: '' });
      setDescription('');
      setSuggestedKeywords([]);
      setSelectedKeywords([]);
      navigate('/dashboard');
    }
    catch {
      setMessage(isEdit ? "Failed to update job" : "Failed to add job");
    }
  }
  return (
    <>
      <div className="container mx-auto py-6 px-4">
        <div className="max-w-4xl mx-auto">
          <form
            onSubmit={handleSubmit}
            className="bg-white p-6 border border-gray-200 rounded-lg shadow-sm"
          >
            {/* Header */}
            <h4 className="mb-6 text-center text-primary font-bold text-2xl">
              {initialData ? "Edit Job" : "Add Job"}
            </h4>

            {/* Position */}
            <div className="mb-4">
              <label htmlFor="position" className="form-label">
                Position <span className="text-red-500">*</span>
              </label>
              <input
                id="position"
                name="position"
                type="text"
                value={form.position}
                onChange={handleChange}
                placeholder="Enter position"
                required
                className="form-input"
              />
            </div>

            {/* Company */}
            <div className="mb-4">
              <label htmlFor="company" className="form-label">
                Company <span className="text-red-500">*</span>
              </label>
              <input
                id="company"
                name="company"
                type="text"
                value={form.company}
                onChange={handleChange}
                placeholder="Enter company name"
                required
                className="form-input"
              />
            </div>

            {/* Status + Location in one row on desktop */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label htmlFor="status" className="form-label">
                  Status
                </label>
                <select
                  id="status"
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                  className="form-input"
                  aria-label="Job application status"
                >
                  <option value="applied">Applied</option>
                  <option value="interviewing">Interviewing</option>
                  <option value="offer">Offer</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div>
                <label htmlFor="location" className="form-label">
                  Location
                </label>
                <input
                  id="location"
                  name="location"
                  type="text"
                  value={form.location}
                  onChange={handleChange}
                  placeholder="Enter location"
                  className="form-input"
                />
              </div>
            </div>

            {/* Notes */}
            <div className="mb-6">
              <label htmlFor="notes" className="form-label">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                value={form.notes}
                onChange={handleChange}
                placeholder="Add any notes..."
                className="form-input"
                rows="3"
              />
            </div>

            {/* Job Description & Keywords */}
            <div className="card border-accent mb-6">
              <div className="bg-accent text-white font-bold p-4">
                Job Description & Keywords
              </div>
              <div className="p-6">
                {/* Job Description */}
                <div className="mb-4">
                  <label htmlFor="description" className="form-label">
                    Job Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    className="form-input"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Paste job description here"
                    rows={5}
                    required
                  />
                </div>

                {/* Suggested Keywords */}
                <div className="mb-4">
                  <label className="form-label">Suggested Keywords</label>
                  {loadingKeywords && (
                    <div className="text-gray-600">Extracting keywords…</div>
                  )}
                  {keywordError && (
                    <div className="text-red-600">{keywordError}</div>
                  )}

                  <div className="flex flex-wrap gap-3">
                    {!loadingKeywords &&
                      suggestedKeywords.map((kw, i) => (
                        <div key={i} className="flex items-center">
                          <input
                            type="checkbox"
                            id={`kw-${i}`}
                            className="w-4 h-4 text-accent border-gray-300 rounded focus:ring-accent mr-2 cursor-pointer"
                            checked={selectedKeywords.includes(kw)}
                            onChange={() => {
                              setSelectedKeywords((prev) =>
                                prev.includes(kw)
                                  ? prev.filter((x) => x !== kw)
                                  : [...prev, kw]
                              );
                            }}
                          />
                          <label
                            htmlFor={`kw-${i}`}
                            className="cursor-pointer"
                          >
                            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">{kw}</span>
                          </label>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex justify-between gap-4">
              {onCancel && (
                <button
                  type="button"
                  onClick={onCancel}
                  className="btn-outline"
                >
                  Cancel
                </button>
              )}
              <button type="submit" className="btn-primary ml-auto">
                {initialData ? "Update Job" : "Add Job"}
              </button>
            </div>

            {/* Success Message */}
            {message && (
              <p className="mt-4 text-center text-emerald-600 font-medium">{message}</p>
            )}
          </form>
        </div>
      </div>
    </>
  );

}
