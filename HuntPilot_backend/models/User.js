const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name:{type: String, required: true},
  email: { type: String, required: true, unique: true },
  password_hash: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
  resumeKeywords: [String],
  resumeFilename: String, 
  resumePath: String 
});

//module.exports = mongoose.model('User', userSchema);
module.exports = mongoose.models.User || mongoose.model('User', userSchema);

