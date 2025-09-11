import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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

  useEffect(() => {
    fetchUserResumeData();
    fetchJobDetails();
  }, [jobId]);

  const fetchUserResumeData = async () => {
    try {
      const response = await fetch('https://aipowered-jobtracker.onrender.com/api/resume/user-data', {
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
      const response = await fetch(`https://aipowered-jobtracker.onrender.com/api/jobs/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const jobData = await response.json();
      localStorage.setItem('currentJobForTailoring', JSON.stringify(jobData));
    } catch (error) {
      console.error('Error fetching job details:', error);
    }
  };

  const generateTailoredResume = async () => {
    setLoading(true);
    try {
      const jobData = JSON.parse(localStorage.getItem('currentJobForTailoring'));
      
      const response = await fetch('https://aipowered-jobtracker.onrender.com/api/resume/tailor', {
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
      
      pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
      
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
                  {/* Professional Summary */}
                  <div className="mb-4">
                    <label className="form-label fw-bold">Professional Summary</label>
                    <textarea
                      className="form-control"
                      rows="5"
                      value={tailoredContent.summary || ''}
                      onChange={(e) => handleContentChange('summary', e.target.value)}
                      placeholder="Professional Summary"
                      style={{resize: 'vertical'}}
                    />
                  </div>

                  {/* Experience Section */}
                  <div className="mb-4">
                    <label className="form-label fw-bold">Experience</label>
                    {tailoredContent.experience?.map((exp, index) => (
                      <div key={index} className="border p-3 mb-3 rounded bg-light">
                        <div className="row">
                          <div className="col-md-6">
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
                          </div>
                          <div className="col-md-6">
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
                          </div>
                        </div>
                        <textarea
                          className="form-control"
                          rows="4"
                          placeholder="Job Description & Achievements"
                          value={exp.description || ''}
                          onChange={(e) => {
                            const newExp = [...tailoredContent.experience];
                            newExp[index].description = e.target.value;
                            handleContentChange('experience', newExp);
                          }}
                          style={{resize: 'vertical'}}
                        />
                      </div>
                    ))}
                  </div>

                  {/* Skills Section */}
                  <div className="mb-4">
                    <label className="form-label fw-bold">Skills</label>
                    <textarea
                      className="form-control"
                      rows="3"
                      value={tailoredContent.skills || ''}
                      onChange={(e) => handleContentChange('skills', e.target.value)}
                      placeholder="Skills (comma-separated)"
                      style={{resize: 'vertical'}}
                    />
                  </div>
                </div>
              ) : (
                <div className="text-center py-5">
                  <i className="fas fa-magic fa-3x text-muted mb-3"></i>
                  <p className="text-muted">Click "Generate Tailored Resume" to start editing your resume for this job.</p>
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
              <div id="resume-preview" className="bg-white p-4 border" style={{minHeight: '800px'}}>
                {tailoredContent ? (
                  <div>
                    {/* Header */}
                    <div className="text-center mb-4 pb-3 border-bottom">
                      <h2 className="mb-2">{resumeData.personalInfo?.name || 'Your Name'}</h2>
                      <p className="mb-1 text-muted">{resumeData.personalInfo?.email}</p>
                      <p className="mb-1 text-muted">{resumeData.personalInfo?.phone}</p>
                      <p className="mb-0 text-muted">{resumeData.personalInfo?.location}</p>
                    </div>

                    {/* Summary */}
                    <div className="mb-4">
                      <h4 className="text-primary border-bottom pb-1">Professional Summary</h4>
                      <p style={{whiteSpace: 'pre-wrap', lineHeight: '1.6'}}>{tailoredContent.summary}</p>
                    </div>

                    {/* Experience */}
                    <div className="mb-4">
                      <h4 className="text-primary border-bottom pb-1">Professional Experience</h4>
                      {tailoredContent.experience?.map((exp, index) => (
                        <div key={index} className="mb-4">
                          <div className="d-flex justify-content-between align-items-start">
                            <div>
                              <h5 className="mb-1">{exp.title}</h5>
                              <h6 className="text-primary mb-1">{exp.company}</h6>
                            </div>
                            <small className="text-muted">{exp.duration}</small>
                          </div>
                          <p style={{whiteSpace: 'pre-wrap', lineHeight: '1.6'}} className="mt-2">
                            {exp.description}
                          </p>
                        </div>
                      ))}
                    </div>

                    {/* Skills */}
                    <div className="mb-4">
                      <h4 className="text-primary border-bottom pb-1">Technical Skills</h4>
                      <p style={{whiteSpace: 'pre-wrap', lineHeight: '1.6'}}>{tailoredContent.skills}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted py-5">
                    <i className="fas fa-file-alt fa-4x mb-3"></i>
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
