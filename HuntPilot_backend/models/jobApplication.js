const mongoose = require('mongoose');
const jobApplicationSchema = new mongoose.Schema({
  userId:{
    type:mongoose.Schema.Types.ObjectId,
    ref:'User',
    required:true
  },
  position:{
    type:String,
    required:true
  },
   company:{
    type:String,
    required:true
  },
   status:{
    type:String,
    enum:['applied','interviewing','offer','rejected'],
    default:'applied'
  },
  location:{
    type:String
  },
  appliedDate:{
    type:Date,
    default:Date.now
  },
  notes:{
    type:String
  },
   keywords: [String],  
})

module.exports = mongoose.model('JobApplication',jobApplicationSchema)

