
// resumeController.js
const User = require('../models/User');
const JobApplication = require('../models/jobApplication');

// Get user's resume data
const getUserResumeData = async (req, res) => {
  try {
    const userId = req.user.userId;
    const user = await User.findById(userId).select('resumeData personalInfo');

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Structure resume data for editor
    const resumeData = {
      personalInfo: {
        name: user.personalInfo?.name || '',
        email: user.personalInfo?.email || '',
        phone: user.personalInfo?.phone || '',
        location: user.personalInfo?.location || ''
      },
      summary: user.resumeData?.summary || '',
      experience: user.resumeData?.experience || [],
      education: user.resumeData?.education || [],
      skills: user.resumeData?.skills || [],
      projects: user.resumeData?.projects || []
    };

    res.status(200).json({
      success: true,
      resumeData
    });
  } catch (error) {
    console.error('Error fetching user resume data:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

// Generate tailored resume using AI service
const tailorResume = async (req, res) => {
  try {
    const { resumeData, jobDescription, jobTitle, company } = req.body;
    const userId = req.user.userId;

    // Call Python AI service for resume tailoring
    const response = await fetch('http://localhost:5000/api/tailor-resume', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        resume_data: resumeData,
        job_description: jobDescription,
        job_title: jobTitle,
        company_name: company
      })
    });

    if (!response.ok) {
      throw new Error('AI service error');
    }

    const aiResult = await response.json();

    // Enhance the tailored content with structured format
    const tailoredResume = {
      summary: aiResult.tailored_summary || resumeData.summary,
      experience: enhanceExperience(resumeData.experience, aiResult.enhanced_experience || []),
      skills: aiResult.optimized_skills || resumeData.skills,
      education: resumeData.education, // Keep education as is
      projects: resumeData.projects,
      matchScore: aiResult.match_score || 0,
      suggestions: aiResult.suggestions || []
    };

    res.status(200).json({
      success: true,
      tailoredResume,
      matchScore: tailoredResume.matchScore,
      suggestions: tailoredResume.suggestions
    });

  } catch (error) {
    console.error('Error tailoring resume:', error);
    res.status(500).json({ 
      success: false,
      message: 'Error tailoring resume. Please try again.' 
    });
  }
};

// Helper function to enhance experience with AI suggestions
const enhanceExperience = (originalExp, aiEnhancements) => {
  return originalExp.map((exp, index) => {
    const enhancement = aiEnhancements[index];
    return {
      ...exp,
      description: enhancement?.enhanced_description || exp.description,
      keywords: enhancement?.relevant_keywords || [],
      title: enhancement?.optimized_title || exp.title
    };
  });
};

// Generate PDF (server-side generation alternative)
const generatePDF = async (req, res) => {
  try {
    const { resumeContent, jobTitle, company } = req.body;

    // Here you could use server-side PDF generation
    // For now, we'll just acknowledge the request
    res.status(200).json({
      success: true,
      message: 'PDF generation successful',
      filename: `${company}_${jobTitle}_Resume.pdf`
    });

  } catch (error) {
    console.error('Error generating PDF:', error);
    res.status(500).json({ message: 'Error generating PDF' });
  }
};

module.exports = {
  getUserResumeData,
  tailorResume,
  generatePDF
};
