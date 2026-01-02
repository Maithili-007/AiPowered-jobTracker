
// resumeRoutes.js
const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const {
  getUserResumeData,
  getResumeContent,
  tailorResume,
  generatePDF
} = require('../controllers/resumeController');

// @route   GET /api/resume/content
// @desc    Get the parsed content from user's uploaded resume file
// @access  Private
router.get('/content', auth, getResumeContent);

// @route   GET /api/resume/user-data
// @desc    Get user's resume data for editing
// @access  Private
router.get('/user-data', auth, getUserResumeData);

// @route   POST /api/resume/tailor
// @desc    Generate tailored resume using AI
// @access  Private
router.post('/tailor', auth, tailorResume);

// @route   POST /api/resume/generate-pdf
// @desc    Generate PDF of tailored resume
// @access  Private
router.post('/generate-pdf', auth, generatePDF);

module.exports = router;
