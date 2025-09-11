const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
require('dotenv').config();
const authRoutes = require('./routes/authRouter');
const jobRoutes = require('./routes/jobRouter');
const analysisRoutes = require('./routes/analysisRouter');
const profileRoutes = require('./routes/profileRouter');
const resumeRoutes = require('./routes/resumeRoutes');
const PORT = process.env.PORT || 5000;

const app = express();
app.use(cors());
app.use(express.json());

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('MongoDB connected'))
  .catch((err) => console.error(err));

app.use('/api/auth', authRoutes);
app.use('/api/jobs', jobRoutes);
app.use('/api/profile', profileRoutes);
app.use('/api/analysis', analysisRoutes);
app.use('/api/resume', resumeRoutes);
app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
