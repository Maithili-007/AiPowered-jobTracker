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
      const res = await axios.get('https://aipowered-jobtracker.onrender.com/api/profile/resume', {
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
      const res = await axios.post('https://aipowered-jobtracker.onrender.com/api/profile/upload-resume', formData, {
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
      const res = await axios.delete('https://aipowered-jobtracker.onrender.com/api/profile/resume', {
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
      const response = await axios.get( 'https://aipowered-jobtracker.onrender.com/api/profile/resume/download', {
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
  <div className="card mb-4 shadow-sm border-0 rounded-3">
    <div className="card-body">
      {resumeFilename ? (
        <>
          {/* Resume Info + Action Buttons */}
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-3">
            <div className="mb-2 mb-md-0">
              <h5 className="card-title mb-1">Uploaded Resume</h5>
              <p className="mb-0 text-muted text-truncate" style={{ maxWidth: "250px" }}>
                {resumeFilename}
              </p>
            </div>
            <div className="d-flex flex-wrap gap-2">
              <button
                className="btn btn-outline-primary btn-sm"
                onClick={handleDownload}
              >
                View Resume
              </button>
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={() => setShowUpload(!showUpload)}
              >
                {showUpload ? "Cancel" : "Update"}
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

      {/* Upload Form */}
      {showUpload && (
        <form onSubmit={handleSubmit} className="bg-light p-3 rounded">
          <div className="mb-3">
            <input
              type="file"
              accept=".txt"
              className="form-control"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>
          <div className="d-flex flex-wrap gap-2">
            <button
              type="submit"
              className="btn btn-success"
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

      {/* Feedback Message */}
      {message && (
        <div className="alert alert-info mt-3 mb-0 text-center">{message}</div>
      )}
    </div>
  </div>
);


}