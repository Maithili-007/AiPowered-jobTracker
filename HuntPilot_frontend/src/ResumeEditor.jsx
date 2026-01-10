import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://aipowered-jobtracker.onrender.com';

const ResumeEditor = () => {
  const { id: jobId } = useParams();
  const navigate = useNavigate();

  // State management
  const [resumeContent, setResumeContent] = useState('');
  const [resumeFilename, setResumeFilename] = useState('');
  const [jobData, setJobData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [noResume, setNoResume] = useState(false);
  const [tailoredContent, setTailoredContent] = useState(null);
  const [tailoring, setTailoring] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  // Fetch the actual resume content from uploaded file
  const fetchResumeContent = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login to access this feature');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/resume/content`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.noResume) {
          setNoResume(true);
        } else {
          setError(data.message || 'Failed to fetch resume');
        }
        return;
      }

      setResumeContent(data.resumeContent || '');
      setResumeFilename(data.resumeFilename || 'resume');
    } catch (err) {
      console.error('Error fetching resume:', err);
      setError('Network error while fetching resume');
    }
  }, []);

  // Fetch job details for tailoring context
  const fetchJobDetails = useCallback(async () => {
    if (!jobId) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setJobData(data);
        localStorage.setItem('currentJobForTailoring', JSON.stringify(data));
      }
    } catch (err) {
      console.error('Error fetching job details:', err);
    }
  }, [jobId]);

  // Initial data loading
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchResumeContent(), fetchJobDetails()]);
      setLoading(false);
    };
    loadData();
  }, [fetchResumeContent, fetchJobDetails]);

  // Handle resume content changes in editor
  const handleContentChange = (e) => {
    setResumeContent(e.target.value);
    // Also update tailored content if in tailored mode
    if (tailoredContent) {
      setTailoredContent(prev => ({
        ...prev,
        editedContent: e.target.value
      }));
    }
  };

  // Generate AI-tailored resume
  const generateTailoredResume = async () => {
    if (!jobData) {
      setError('Job details not loaded. Please try again.');
      return;
    }

    if (!resumeContent || !resumeContent.trim()) {
      setError('No resume content found. Please ensure your resume is loaded.');
      return;
    }

    setTailoring(true);
    setError(null); // Clear any previous errors
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/resume/tailor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          resumeData: { rawContent: resumeContent },
          jobDescription: jobData.description || jobData.jobDescription || '',
          jobTitle: jobData.position || jobData.title || '',
          company: jobData.company || ''
        })
      });

      const result = await response.json();

      if (!response.ok) {
        // Handle HTTP error responses
        setError(result.message || 'Server error occurred. Please try again.');
        return;
      }

      if (result.success && result.tailoredResume) {
        // Format the tailored content for display
        const formattedContent = formatTailoredContent(result.tailoredResume, resumeContent);
        setTailoredContent({
          ...result.tailoredResume,
          editedContent: formattedContent
        });
        setResumeContent(formattedContent);
      } else {
        setError(result.message || 'Failed to generate tailored resume. Please try again.');
      }
    } catch (err) {
      console.error('Error tailoring resume:', err);
      setError('Network error while generating tailored resume. Please check your connection and try again.');
    } finally {
      setTailoring(false);
    }
  };

  // Format AI-tailored content into readable text
  // Handles both structured data (summary, experience, skills) and raw content scenarios
  const formatTailoredContent = (tailored, originalContent = '') => {
    let content = '';

    // Add the tailored professional summary if available
    if (tailored.summary) {
      content += `PROFESSIONAL SUMMARY\n${'='.repeat(50)}\n${tailored.summary}\n\n`;
    }

    // Add experience section if we have structured experience data
    if (tailored.experience && tailored.experience.length > 0) {
      content += `EXPERIENCE\n${'='.repeat(50)}\n`;
      tailored.experience.forEach(exp => {
        content += `${exp.title || exp.optimized_title || 'Position'}\n`;
        content += `${exp.company || 'Company'} | ${exp.duration || ''}\n`;
        content += `${exp.enhanced_description || exp.description || ''}\n`;
        // Show relevant keywords if available
        if (exp.relevant_keywords && exp.relevant_keywords.length > 0) {
          content += `Keywords: ${exp.relevant_keywords.join(', ')}\n`;
        }
        content += '\n';
      });
    }

    // Add skills section
    if (tailored.skills) {
      content += `SKILLS\n${'='.repeat(50)}\n`;
      if (Array.isArray(tailored.skills)) {
        content += tailored.skills.join(', ');
      } else {
        content += tailored.skills;
      }
      content += '\n\n';
    }

    // Add education section if available
    if (tailored.education && tailored.education.length > 0) {
      content += `EDUCATION\n${'='.repeat(50)}\n`;
      tailored.education.forEach(edu => {
        content += `${edu.degree || ''} - ${edu.institution || ''}\n`;
        content += `${edu.year || ''}\n\n`;
      });
    }

    // Add match details if available (from AI analysis)
    if (tailored.matchDetails) {
      content += `\nMATCH ANALYSIS\n${'='.repeat(50)}\n`;
      if (tailored.matchDetails.matched_skills && tailored.matchDetails.matched_skills.length > 0) {
        content += `✓ Matched Skills: ${tailored.matchDetails.matched_skills.join(', ')}\n`;
      }
      if (tailored.matchDetails.missing_skills && tailored.matchDetails.missing_skills.length > 0) {
        content += `✗ Skills to Add: ${tailored.matchDetails.missing_skills.join(', ')}\n`;
      }
      if (tailored.matchDetails.extra_skills && tailored.matchDetails.extra_skills.length > 0) {
        content += `★ Bonus Skills: ${tailored.matchDetails.extra_skills.join(', ')}\n`;
      }
    }

    // If we have content, use it; otherwise fall back to original resume
    return content.trim() || originalContent;
  };

  // Download resume as PDF
  const downloadPDF = async () => {
    const previewElement = document.getElementById('resume-preview');
    if (!previewElement) return;

    setDownloadingPdf(true);
    try {
      const canvas = await html2canvas(previewElement, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false
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

      // Handle multi-page documents
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      // Generate filename
      const companyName = jobData?.company || 'Resume';
      const positionTitle = jobData?.position || jobData?.title || '';
      const fileName = `${companyName}${positionTitle ? '_' + positionTitle : ''}_Resume.pdf`.replace(/\s+/g, '_');

      pdf.save(fileName);
    } catch (err) {
      console.error('Error generating PDF:', err);
      setError('Error generating PDF. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-gray-600">Loading your resume...</p>
        </div>
      </div>
    );
  }

  // No resume uploaded state
  if (noResume) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <svg className="w-16 h-16 text-yellow-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Resume Found</h3>
            <p className="text-gray-600 mb-4">
              Please upload your resume in the Profile section first to use the Resume Editor.
            </p>
            <div className="flex gap-3 justify-center">
              <button
                className="btn-secondary"
                onClick={() => navigate(-1)}
              >
                Go Back
              </button>
              <button
                className="btn-primary"
                onClick={() => navigate('/profile')}
              >
                Go to Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !resumeContent) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <svg className="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className="text-xl font-semibold text-red-800 mb-2">Error</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              className="btn-secondary"
              onClick={() => navigate(-1)}
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header Section */}
      <div className="mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-primary">Resume Editor</h2>
            {jobData && (
              <p className="text-gray-600 mt-1">
                Tailoring for: <span className="font-medium">{jobData.position || jobData.title}</span>
                {jobData.company && <span> at {jobData.company}</span>}
              </p>
            )}
            {resumeFilename && (
              <p className="text-sm text-gray-500 mt-1">
                Source: {resumeFilename}
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              className="btn-secondary"
              onClick={() => navigate(-1)}
            >
              ← Back
            </button>
            {!tailoredContent && jobData && (
              <button
                className="btn-primary"
                onClick={generateTailoredResume}
                disabled={tailoring}
              >
                {tailoring ? (
                  <>
                    <span className="animate-spin inline-block mr-2">⟳</span>
                    Tailoring...
                  </>
                ) : (
                  '✨ AI Tailor Resume'
                )}
              </button>
            )}
            <button
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
              onClick={downloadPDF}
              disabled={downloadingPdf || !resumeContent}
            >
              {downloadingPdf ? 'Generating...' : '📥 Download PDF'}
            </button>
          </div>
        </div>
      </div>

      {/* AI Match Score Banner */}
      {tailoredContent?.matchScore && (
        <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold text-blue-800">AI Match Analysis</h4>
              <p className="text-sm text-blue-600">Resume tailored for better job match</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-blue-600">{tailoredContent.matchScore}%</div>
              <div className="text-sm text-blue-500">Match Score</div>
            </div>
          </div>
          {tailoredContent.suggestions && tailoredContent.suggestions.length > 0 && (
            <div className="mt-3 pt-3 border-t border-blue-200">
              <p className="text-sm font-medium text-blue-700 mb-1">Suggestions:</p>
              <ul className="text-sm text-blue-600 list-disc list-inside">
                {tailoredContent.suggestions.slice(0, 3).map((suggestion, i) => (
                  <li key={i}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Error Toast */}
      {error && resumeContent && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center justify-between">
          <p className="text-red-600">{error}</p>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">✕</button>
        </div>
      )}

      {/* Main Editor Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Editor Panel */}
        <div className="card">
          <div className="bg-primary text-white p-4 rounded-t-lg">
            <h5 className="font-semibold text-lg">✏️ Editor</h5>
            <p className="text-sm opacity-80">Edit your resume content below</p>
          </div>
          <div className="p-4">
            <textarea
              className="w-full h-[65vh] p-4 border border-gray-200 rounded-lg font-mono text-sm resize-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              value={resumeContent}
              onChange={handleContentChange}
              placeholder="Your resume content will appear here..."
              spellCheck="false"
            />
          </div>
        </div>

        {/* Preview Panel */}
        <div className="card">
          <div className="bg-primary text-white p-4 rounded-t-lg">
            <h5 className="font-semibold text-lg">👁️ Preview</h5>
            <p className="text-sm opacity-80">Live preview of your resume</p>
          </div>
          <div className="p-4 max-h-[75vh] overflow-y-auto bg-gray-50">
            <div
              id="resume-preview"
              className="bg-white p-8 border border-gray-200 shadow-sm min-h-[800px] rounded"
              style={{ fontFamily: 'Georgia, serif' }}
            >
              {resumeContent ? (
                <div className="prose max-w-none">
                  {resumeContent.split('\n').map((line, idx) => {
                    // Style section headers (lines with ===)
                    if (line.includes('===')) {
                      return null;
                    }
                    // Style section titles (all caps followed by ===)
                    const prevLine = resumeContent.split('\n')[idx - 1];
                    const nextLine = resumeContent.split('\n')[idx + 1];
                    if (nextLine && nextLine.includes('===')) {
                      return (
                        <h2 key={idx} className="text-lg font-bold text-primary border-b-2 border-primary pb-1 mt-6 mb-3">
                          {line}
                        </h2>
                      );
                    }
                    // Empty lines
                    if (!line.trim()) {
                      return <div key={idx} className="h-2" />;
                    }
                    // Regular lines
                    return (
                      <p key={idx} className="mb-1 text-gray-800 leading-relaxed">
                        {line}
                      </p>
                    );
                  })}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">
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
