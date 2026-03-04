const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });
const authRoutes = require('./routes/authRouter');
const jobRoutes = require('./routes/jobRouter');
const analysisRoutes = require('./routes/analysisRouter');
const profileRoutes = require('./routes/profileRouter');
const resumeRoutes = require('./routes/resumeRoutes');
const PORT = process.env.PORT || 5000;

const app = express();
const allowedOrigins = [
  process.env.FRONTEND_URL,
  'http://localhost:5173',
  'http://127.0.0.1:5173',
  'http://localhost:3000',
  'http://127.0.0.1:3000',
].filter(Boolean);

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      return callback(null, true);
    }
    return callback(new Error('Not allowed by CORS'));
  },
}));
app.use(express.json());

if (process.env.MONGO_URI) {
  mongoose.connect(process.env.MONGO_URI)
    .then(() => console.log('MongoDB connected'))
    .catch((err) => console.error('MongoDB connection error:', err.message));
} else {
  console.warn('MONGO_URI is not set. Server started without database connection.');
}

app.use('/api/auth', authRoutes);
app.use('/api/jobs', jobRoutes);
app.use('/api/profile', profileRoutes);
app.use('/api/analysis', analysisRoutes);
app.use('/api/resume', resumeRoutes);
app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
