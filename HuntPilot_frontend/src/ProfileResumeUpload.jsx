import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import AuthContext from './AuthContext';

export default function ProfileResumeUpload() {
  const { token } = useContext(AuthContext);
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
      //setResumeFilename(file.name);
      setResumeFilename(res.data.resumeFilename);
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
      const response = await axios.get('https://aipowered-jobtracker.onrender.com/api/profile/resume/download', {
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
    <div className="card mb-6">
      <div className="p-6">
        {resumeFilename ? (
          <>
            {/* Resume Info + Action Buttons */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
              <div>
                <h5 className="font-semibold text-lg text-gray-900 mb-1">Uploaded Resume</h5>
                <p className="text-gray-600 truncate max-w-xs">
                  {resumeFilename}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  className="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-lg text-sm font-medium transition-colors"
                  onClick={handleDownload}
                >
                  View Resume
                </button>
                <button
                  className="px-4 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-lg text-sm font-medium transition-colors"
                  onClick={() => setShowUpload(!showUpload)}
                >
                  {showUpload ? "Cancel" : "Update"}
                </button>
                <button
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
                  onClick={handleDelete}
                >
                  Delete
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center mb-4">
            <p className="text-gray-500 mb-3">No resume uploaded yet.</p>
            <button
              className="btn-primary"
              onClick={() => setShowUpload(true)}
            >
              Upload Resume
            </button>
          </div>
        )}

        {/* Upload Form */}
        {showUpload && (
          <form onSubmit={handleSubmit} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="mb-4">
              <input
                type="file"
                accept=".pdf,.txt"
                className="form-input"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="submit"
                className="btn-primary"
                disabled={!file}
              >
                Upload
              </button>
              <button
                type="button"
                className="btn-outline"
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
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 text-blue-800 rounded-lg text-center">{message}</div>
        )}
      </div>
    </div>
  );

}