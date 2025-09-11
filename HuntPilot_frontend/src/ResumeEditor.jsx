
// ResumeEditor.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';

const ResumeEditor = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [resumeData, setResumeData] = useState({
    personalInfo: {},
    summary: '',
    experience: [],
    education: [],
    skills: []
  });
  const [tailoredContent, setTailoredContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchUserResumeData();
    fetchJobDetails();
  }, [jobId]);

  const fetchUserResumeData = async () => {
    try {
      const response = await fetch('/api/resume/user-data', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setResumeData(data.resumeData);
    } catch (error) {
      console.error('Error fetching resume data:', error);
    }
  };

  const fetchJobDetails = async () => {
    try {
      const response = await fetch(`/api/jobs/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const jobData = await response.json();
      // Store job data for tailoring
      localStorage.setItem('currentJobForTailoring', JSON.stringify(jobData));
    } catch (error) {
      console.error('Error fetching job details:', error);
    }
  };

  const generateTailoredResume = async () => {
    setLoading(true);
    try {
      const jobData = JSON.parse(localStorage.getItem('currentJobForTailoring'));

      const response = await fetch('/api/resume/tailor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          resumeData,
          jobDescription: jobData.description,
          jobTitle: jobData.position,
          company: jobData.company
        })
      });

      const tailored = await response.json();
      setTailoredContent(tailored.tailoredResume);
      setIsEditing(true);
    } catch (error) {
      console.error('Error generating tailored resume:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (field, value) => {
    setTailoredContent(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const downloadPDF = async () => {
    const element = document.getElementById('resume-preview');

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');

      const imgWidth = 210;
      const pageHeight = 295;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      const jobData = JSON.parse(localStorage.getItem('currentJobForTailoring'));
      const fileName = `${jobData.company}_${jobData.position}_Resume.pdf`;

      pdf.save(fileName);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  return (
    <div className="container-fluid">
      <div className="row">
        <div className="col-12">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2>Resume Tailoring</h2>
            <div>
              <button 
                className="btn btn-secondary me-2" 
                onClick={() => navigate(-1)}
              >
                Back
              </button>
              {!tailoredContent && (
                <button 
                  className="btn btn-primary me-2" 
                  onClick={generateTailoredResume}
                  disabled={loading}
                >
                  {loading ? 'Generating...' : 'Generate Tailored Resume'}
                </button>
              )}
              {tailoredContent && (
                <button 
                  className="btn btn-success" 
                  onClick={downloadPDF}
                >
                  Download PDF
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        {/* Editor Panel */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5>Resume Editor</h5>
            </div>
            <div className="card-body" style={{maxHeight: '80vh', overflowY: 'auto'}}>
              {tailoredContent ? (
                <div>
                  {/* Personal Summary */}
                  <div className="mb-4">
                    <label className="form-label">Professional Summary</label>
                    <ReactQuill
                      theme="snow"
                      value={tailoredContent.summary || ''}
                      onChange={(value) => handleContentChange('summary', value)}
                      style={{height: '120px', marginBottom: '50px'}}
                    />
                  </div>

                  {/* Experience Section */}
                  <div className="mb-4">
                    <label className="form-label">Experience</label>
                    {tailoredContent.experience?.map((exp, index) => (
                      <div key={index} className="border p-3 mb-3 rounded">
                        <input
                          type="text"
                          className="form-control mb-2"
                          placeholder="Job Title"
                          value={exp.title || ''}
                          onChange={(e) => {
                            const newExp = [...tailoredContent.experience];
                            newExp[index].title = e.target.value;
                            handleContentChange('experience', newExp);
                          }}
                        />
                        <input
                          type="text"
                          className="form-control mb-2"
                          placeholder="Company"
                          value={exp.company || ''}
                          onChange={(e) => {
                            const newExp = [...tailoredContent.experience];
                            newExp[index].company = e.target.value;
                            handleContentChange('experience', newExp);
                          }}
                        />
                        <ReactQuill
                          theme="snow"
                          value={exp.description || ''}
                          onChange={(value) => {
                            const newExp = [...tailoredContent.experience];
                            newExp[index].description = value;
                            handleContentChange('experience', newExp);
                          }}
                          style={{height: '100px', marginBottom: '50px'}}
                        />
                      </div>
                    ))}
                  </div>

                  {/* Skills Section */}
                  <div className="mb-4">
                    <label className="form-label">Skills</label>
                    <ReactQuill
                      theme="snow"
                      value={tailoredContent.skills || ''}
                      onChange={(value) => handleContentChange('skills', value)}
                      style={{height: '80px', marginBottom: '50px'}}
                    />
                  </div>
                </div>
              ) : (
                <div className="text-center py-5">
                  <p>Click "Generate Tailored Resume" to start editing your resume for this job.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5>Resume Preview</h5>
            </div>
            <div className="card-body" style={{maxHeight: '80vh', overflowY: 'auto'}}>
              <div id="resume-preview" className="bg-white p-4" style={{minHeight: '800px'}}>
                {tailoredContent ? (
                  <div>
                    {/* Header */}
                    <div className="text-center mb-4 border-bottom pb-3">
                      <h3>{resumeData.personalInfo?.name || 'Your Name'}</h3>
                      <p className="mb-1">{resumeData.personalInfo?.email}</p>
                      <p className="mb-1">{resumeData.personalInfo?.phone}</p>
                    </div>

                    {/* Summary */}
                    <div className="mb-4">
                      <h5 className="text-primary">Professional Summary</h5>
                      <div dangerouslySetInnerHTML={{__html: tailoredContent.summary}} />
                    </div>

                    {/* Experience */}
                    <div className="mb-4">
                      <h5 className="text-primary">Experience</h5>
                      {tailoredContent.experience?.map((exp, index) => (
                        <div key={index} className="mb-3">
                          <h6 className="mb-1">{exp.title} - {exp.company}</h6>
                          <p className="text-muted small">{exp.duration}</p>
                          <div dangerouslySetInnerHTML={{__html: exp.description}} />
                        </div>
                      ))}
                    </div>

                    {/* Skills */}
                    <div className="mb-4">
                      <h5 className="text-primary">Skills</h5>
                      <div dangerouslySetInnerHTML={{__html: tailoredContent.skills}} />
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted">
                    <p>Resume preview will appear here</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeEditor;
