const express = require('express');
const axios = require('axios');
const analysisRouter = express.Router();

analysisRouter.post('/extract', async (req, res) => {
  try {
    const { description } = req.body;
    const { data } = await axios.post('http://localhost:5001/extract-keywords', { description });
    res.json(data);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Analysis failed' });
  }
});

module.exports = analysisRouter;

