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
    <div className="container mx-auto px-4 py-6">
      <div className="mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h2 className="text-2xl font-bold text-primary">Resume Tailoring</h2>
          <div className="flex flex-wrap gap-2">
            <button
              className="btn-secondary"
              onClick={() => navigate(-1)}
            >
              Back
            </button>
            {!tailoredContent && (
              <button
                className="btn-primary"
                onClick={generateTailoredResume}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Tailored Resume'}
              </button>
            )}
            {tailoredContent && (
              <button
                className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                onClick={downloadPDF}
              >
                Download PDF
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Editor Panel */}
        <div className="card">
          <div className="bg-primary text-white p-4">
            <h5 className="font-semibold text-lg">Resume Editor</h5>
          </div>
          <div className="p-6 max-h-[80vh] overflow-y-auto">
            {tailoredContent ? (
              <div>
                {/* Professional Summary */}
                <div className="mb-6">
                  <label className="form-label font-bold">Professional Summary</label>
                  <textarea
                    className="form-input resize-y"
                    rows="5"
                    value={tailoredContent.summary || ''}
                    onChange={(e) => handleContentChange('summary', e.target.value)}
                    placeholder="Professional Summary"
                  />
                </div>

                {/* Experience Section */}
                <div className="mb-6">
                  <label className="form-label font-bold">Experience</label>
                  {tailoredContent.experience?.map((exp, index) => (
                    <div key={index} className="border border-gray-200 bg-gray-50 p-4 mb-4 rounded-lg">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                        <input
                          type="text"
                          className="form-input"
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
                          className="form-input"
                          placeholder="Company"
                          value={exp.company || ''}
                          onChange={(e) => {
                            const newExp = [...tailoredContent.experience];
                            newExp[index].company = e.target.value;
                            handleContentChange('experience', newExp);
                          }}
                        />
                      </div>
                      <textarea
                        className="form-input resize-y"
                        rows="4"
                        placeholder="Job Description & Achievements"
                        value={exp.description || ''}
                        onChange={(e) => {
                          const newExp = [...tailoredContent.experience];
                          newExp[index].description = e.target.value;
                          handleContentChange('experience', newExp);
                        }}
                      />
                    </div>
                  ))}
                </div>

                {/* Skills Section */}
                <div className="mb-6">
                  <label className="form-label font-bold">Skills</label>
                  <textarea
                    className="form-input resize-y"
                    rows="3"
                    value={tailoredContent.skills || ''}
                    onChange={(e) => handleContentChange('skills', e.target.value)}
                    placeholder="Skills (comma-separated)"
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">Click "Generate Tailored Resume" to start editing your resume for this job.</p>
              </div>
            )}
          </div>
        </div>

        {/* Preview Panel */}
        <div className="card">
          <div className="bg-primary text-white p-4">
            <h5 className="font-semibold text-lg">Resume Preview</h5>
          </div>
          <div className="p-6 max-h-[80vh] overflow-y-auto">
            <div id="resume-preview" className="bg-white p-6 border border-gray-200 min-h-[800px]">
              {tailoredContent ? (
                <div>
                  {/* Header */}
                  <div className="text-center mb-6 pb-4 border-b-2 border-gray-300">
                    <h2 className="text-3xl font-bold mb-2">{resumeData.personalInfo?.name || 'Your Name'}</h2>
                    <p className="text-gray-600 mb-1">{resumeData.personalInfo?.email}</p>
                    <p className="text-gray-600 mb-1">{resumeData.personalInfo?.phone}</p>
                    <p className="text-gray-600">{resumeData.personalInfo?.location}</p>
                  </div>

                  {/* Summary */}
                  <div className="mb-6">
                    <h4 className="text-accent font-bold text-xl border-b border-gray-300 pb-1 mb-3">Professional Summary</h4>
                    <p className="whitespace-pre-wrap leading-relaxed">{tailoredContent.summary}</p>
                  </div>

                  {/* Experience */}
                  <div className="mb-6">
                    <h4 className="text-accent font-bold text-xl border-b border-gray-300 pb-1 mb-3">Professional Experience</h4>
                    {tailoredContent.experience?.map((exp, index) => (
                      <div key={index} className="mb-5">
                        <div className="flex justify-between items-start">
                          <div>
                            <h5 className="font-bold text-lg mb-1">{exp.title}</h5>
                            <h6 className="text-accent font-semibold mb-1">{exp.company}</h6>
                          </div>
                          <small className="text-gray-600">{exp.duration}</small>
                        </div>
                        <p className="whitespace-pre-wrap leading-relaxed mt-2">
                          {exp.description}
                        </p>
                      </div>
                    ))}
                  </div>

                  {/* Skills */}
                  <div className="mb-6">
                    <h4 className="text-accent font-bold text-xl border-b border-gray-300 pb-1 mb-3">Technical Skills</h4>
                    <p className="whitespace-pre-wrap leading-relaxed">{tailoredContent.skills}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-400 py-12">
                  <p>Resume preview will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeEditor;
