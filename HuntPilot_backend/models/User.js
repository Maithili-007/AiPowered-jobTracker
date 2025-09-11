const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name:{type: String, required: true},
  email: { type: String, required: true, unique: true },
  password_hash: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
  resumeKeywords: [String],
  resumeFilename: String, 
  resumePath: String,
   resumeData: {
    summary: { type: String, default: '' },
    experience: [{
      title: { type: String },
      company: { type: String },
      duration: { type: String },
      description: { type: String }
    }],
    education: [{
      degree: { type: String },
      institution: { type: String },
      year: { type: String }
    }],
    skills: { type: String, default: '' },
    projects: [{
      name: { type: String },
      description: { type: String },
      technologies: { type: String }
    }]
  },
  personalInfo: {
    name: { type: String },
    email: { type: String },
    phone: { type: String },
    location: { type: String }
  }
});

//module.exports = mongoose.model('User', userSchema);
module.exports = mongoose.models.User || mongoose.model('User', userSchema);

