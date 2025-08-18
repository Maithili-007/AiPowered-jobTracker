import React, { useState, useContext,useEffect } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';
import { useNavigate, NavLink } from 'react-router-dom';

export default function AddJob({ initialData, onSuccess, onCancel }){
  const[form,setForm]=useState({position:'',company: '', status: 'applied', location: '', notes: '',...initialData || {}});
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

  const handleChange= (e)=>{
    setForm({...form,[e.target.name]:e.target.value});//curly brackets because you're creating a new object.
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
      const resp = await fetch('https://aipowered-jobtracker-1.onrender.com/extract-keywords', {
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

  const handleSubmit= async (e)=>{
    e.preventDefault();
    const isEdit = !!(initialData && initialData._id);
    const url = isEdit?`https://aipowered-jobtracker.onrender.com/api/jobs/${initialData._id}`: 'https://aipowered-jobtracker.onrender.com/api/jobs';
    const method = isEdit? "put":"post";

    const payload = {
      ...form,
      description,
      keywords: selectedKeywords
    };


    try{
      const res = await axios[method](url,payload,{headers:{Authorization:`Bearer ${token}`}});
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
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-md-10 col-lg-8">
          <form
            onSubmit={handleSubmit}
            className="p-4 border rounded shadow-sm bg-white"
          >
            {/* Header */}
            <h4 className="mb-4 text-center">
              {initialData ? "Edit Job" : "Add Job"}
            </h4>

            {/* Position */}
            <div className="mb-3">
              <label htmlFor="position" className="form-label">
                Position <span className="text-danger">*</span>
              </label>
              <input
                id="position"
                name="position"
                type="text"
                value={form.position}
                onChange={handleChange}
                placeholder="Enter position"
                required
                className="form-control"
              />
            </div>

            {/* Company */}
            <div className="mb-3">
              <label htmlFor="company" className="form-label">
                Company <span className="text-danger">*</span>
              </label>
              <input
                id="company"
                name="company"
                type="text"
                value={form.company}
                onChange={handleChange}
                placeholder="Enter company name"
                required
                className="form-control"
              />
            </div>

            {/* Status + Location in one row on desktop */}
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <label htmlFor="status" className="form-label">
                  Status
                </label>
                <select
                  id="status"
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                  className="form-select"
                  aria-label="Job application status"
                >
                  <option value="applied">Applied</option>
                  <option value="interviewing">Interviewing</option>
                  <option value="offer">Offer</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div className="col-12 col-md-6 mb-3">
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
                  className="form-control"
                />
              </div>
            </div>

            {/* Notes */}
            <div className="mb-4">
              <label htmlFor="notes" className="form-label">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                value={form.notes}
                onChange={handleChange}
                placeholder="Add any notes..."
                className="form-control"
                rows="3"
              />
            </div>

            {/* Job Description & Keywords */}
            <div className="card mb-4">
              <div className="card-header bg-light">
                <h5 className="mb-0">Job Description & Keywords</h5>
              </div>
              <div className="card-body">
                {/* Job Description */}
                <div className="mb-3">
                  <label htmlFor="description" className="form-label">
                    Job Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    className="form-control"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Paste job description here"
                    rows={5}
                    required
                  />
                </div>

                {/* Suggested Keywords */}
                <div className="mb-3">
                  <label className="form-label">Suggested Keywords</label>
                  {loadingKeywords && (
                    <div className="text-info">Extracting keywords…</div>
                  )}
                  {keywordError && (
                    <div className="text-danger">{keywordError}</div>
                  )}

                  <div className="d-flex flex-wrap">
                    {!loadingKeywords &&
                      suggestedKeywords.map((kw, i) => (
                        <div key={i} className="form-check me-3 mb-2">
                          <input
                            type="checkbox"
                            id={`kw-${i}`}
                            className="form-check-input"
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
                            className="form-check-label"
                          >
                            <span className="badge bg-secondary">{kw}</span>
                          </label>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Buttons */}
            <div className="d-flex justify-content-between">
              {onCancel && (
                <button
                  type="button"
                  onClick={onCancel}
                  className="btn btn-outline-secondary"
                >
                  Cancel
                </button>
              )}
              <button type="submit" className="btn btn-primary ms-auto">
                {initialData ? "Update Job" : "Add Job"}
              </button>
            </div>

            {/* Success Message */}
            {message && (
              <p className="mt-3 text-center text-success">{message}</p>
            )}
          </form>
        </div>
      </div>
    </div>
  </>
);


}

