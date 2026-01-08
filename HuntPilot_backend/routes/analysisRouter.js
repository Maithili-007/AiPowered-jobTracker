const express = require('express');
const axios = require('axios');
const analysisRouter = express.Router();

analysisRouter.post('/extract', async (req, res) => {
  try {
    const { description } = req.body;
    const ANALYSIS_SERVICE_URL = process.env.ANALYSIS_SERVICE_URL || 'https://aipowered-jobtracker-1.onrender.com';
    const { data } = await axios.post(`${ANALYSIS_SERVICE_URL}/extract-keywords`, { description });
    res.json(data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Analysis failed' });
  }
});

module.exports = analysisRouter;

