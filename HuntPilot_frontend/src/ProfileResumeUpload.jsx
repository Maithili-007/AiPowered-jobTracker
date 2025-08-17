import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';

export default function ProfileResumeUpload(){
  const {token} = useContext(AuthContext);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [resumeFilename, setResumeFilename] = useState('');
  const [showUpload, setShowUpload] = useState(false);

 useEffect(() => {
  async function fetchResume() {
    try {
      const res = await axios.get('/api/profile/resume', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setResumeFilename(res.data.resumeFilename);
    } catch {
      setMessage('Failed to load resume info');
    }
  }
  if (token) {
    fetchResume();
  }
}, [token]);

 const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();//creates object
    formData.append('resume', file);//Adds the file to the form data under the key "resume"

    try {
      const res = await axios.post('/api/profile/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });
      setMessage(res.data.message);
      setResumeFilename(file.name);
      setFile(null);
      setShowUpload(false);
    } catch {
      setMessage('Failed to upload resume');
    }
  };

  const handleDelete = async () => {
    try {
      const res = await axios.delete('/api/profile/resume', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(res.data.message);
      setResumeFilename('');
      setFile(null);
      setShowUpload(false);
    } catch {
      setMessage('Failed to delete resume');
    }
  };

   const handleDownload = async () => {
    try {
      const response = await axios.get( 'http://localhost:5000/api/profile/resume/download', {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'//tells Axios to handle the file as binary data
      });
      const blob = new Blob([response.data], { type: response.headers['content-type'] });//Wraps the raw data in a Blob so the browser can treat it like a real file
      const url = URL.createObjectURL(blob);//Creates a temporary file URL
      const link = document.createElement('a');
      link.href = url;
      link.download = resumeFilename; 
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      setMessage('Failed to download resume');
    }
  };

  return (
    <div className="card mb-4 shadow-sm">
      <div className="card-body">
        {resumeFilename ? (
          <>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 className="card-title mb-1">Uploaded Resume</h5>
                <p className="mb-0 text-truncate" style={{ maxWidth: '70%' }}>
                  {resumeFilename}
                </p>
              </div>             
              <div>
                  <button
                  className="btn btn-outline-primary btn-sm me-2"
                  onClick={handleDownload}
                >
                  View Resume
                </button>
                <button
                  className="btn btn-outline-secondary btn-sm me-2"
                  onClick={() => setShowUpload(!showUpload)}
                >
                  {showUpload ? 'Cancel' : 'Update'}
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={handleDelete}
                >
                  Delete
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center mb-3">
            <p className="text-muted">No resume uploaded yet.</p>
            <button
              className="btn btn-primary"
              onClick={() => setShowUpload(true)}
            >
              Upload Resume
            </button>
          </div>
        )}

        {showUpload && (
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <input
                type="file"
                accept=".txt"
                className="form-control"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </div>
            <div className="d-flex">
              <button
                type="submit"
                className="btn btn-success me-2"
                disabled={!file}
              >
                Upload
              </button>
              <button
                type="button"
                className="btn btn-outline-secondary"
                onClick={() => {
                  setShowUpload(false);
                  setFile(null);
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {message && (
          <div className="alert alert-info mt-3 mb-0">{message}</div>
        )}
      </div>
    </div>
  );

}