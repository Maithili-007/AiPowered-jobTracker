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
      const resp = await fetch('/api/analysis/extract', {
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
  <form onSubmit={handleSubmit} className="p-4 border rounded shadow-sm" style={{ maxWidth: '500px', margin: 'auto' }}>
     <h4 className="mb-3">{initialData ? "Edit Job" : "Add Job"}</h4>
    <div className="mb-3">
      <label htmlFor="position" className="form-label">Position <span className="text-danger">*</span></label>
      <input
        id="position"
        name="position"
        type="text"
        value={form.position}//evaluate this JavaScript expression.
        onChange={handleChange}
        placeholder="Position"
        required
        className="form-control"
      />
    </div>

    <div className="mb-3">
      <label htmlFor="company" className="form-label">Company <span className="text-danger">*</span></label>
      <input
        id="company"
        name="company"
        type="text"
        value={form.company}
        onChange={handleChange}
        placeholder="Company"
        required
        className="form-control"
      />
    </div>

    <div className="mb-3">
      <label htmlFor="status" className="form-label">Status</label>
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

    <div className="mb-3">
      <label htmlFor="location" className="form-label">Location</label>
      <input
        id="location"
        name="location"
        type="text"
        value={form.location}
        onChange={handleChange}
        placeholder="Location"
        className="form-control"
      />
    </div>

    <div className="mb-4">
      <label htmlFor="notes" className="form-label">Notes</label>
      <textarea
        id="notes"
        name="notes"
        value={form.notes}
        onChange={handleChange}
        placeholder="Notes"
        className="form-control"
        rows="4"
      />
    </div>

   {/* Job Description & Keywords Section */}
<div className="card mb-4">
  <div className="card-header">
    <h5 className="mb-0">Job Description & Keywords</h5>
  </div>
  <div className="card-body">
    {/* ❶ Job Description Field */}
    <div className="mb-3">
      <label htmlFor="description" className="form-label">
        Job Description
      </label>
      <textarea
        id="description"
        name="description"
        className="form-control"
        value={description}
        onChange={e => setDescription(e.target.value)}
        placeholder="Paste job description here"
        rows={6}
        required
      />
    </div>

    {/* ❸ Suggested Keywords Picker */}
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
                  setSelectedKeywords(prev =>
                    prev.includes(kw)
                      ? prev.filter(x => x !== kw)
                      : [...prev, kw]
                  );
                }}
              />
              <label htmlFor={`kw-${i}`} className="form-check-label">
                <span className="badge bg-secondary">{kw}</span>
              </label>
            </div>
          ))}
      </div>
    </div>
  </div>
</div>


    <div className="d-flex justify-content-between">
        {onCancel && (
          <button type="button" onClick={onCancel} className="btn btn-secondary">
            Cancel
          </button>
        )}
        <button type="submit" className="btn btn-primary ms-auto">
          {initialData ? "Update Job" : "Add Job"}
        </button>
      </div>

    {message && (
      <p className="mt-3 text-center text-success">{message}</p>
    )}
  </form>
  </>
);

}

