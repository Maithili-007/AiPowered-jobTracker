const JobApplication = require('../models/jobApplication');
const User = require('../models/User');

//add new job
exports.createJob = async (req,res,next)=>{
try{
const job = new JobApplication({
  userId:req.user.id,
  ...req.body
});
const newJob = await job.save();
res.status(201).json(newJob);
}
catch (err) {
res.status(500).json({ message: 'Failed to create job', error: err.message });
}
};

//get all jobs
exports.getJobs = async (req,res,next)=>{
  try{
  const jobs =await JobApplication.find({userId:req.user.id}).sort({appliedDate:-1});
 res.json(jobs);
  }
  catch (err) {
    res.status(500).json({ message: 'Failed to fetch jobs', error: err.message });
}
};

//single job detail
exports.getJobById = async (req,res,next)=>{
  try{
    const job = await JobApplication.findOne({_id:req.params.id,userId:req.user.id});
    if(!job){
      return res.status(404).json({ message: 'Job not found' });
    }
    res.json(job);
  }
  catch(err){
    res.status(500).json({ message: 'Failed to fetch job', error: err.message });
  }
};

//edit jon
exports.updateJob = async(req,res,next)=>{
  try{
    const updateJob = await JobApplication.findOneAndUpdate({_id:req.params.id,userId:req.user.id},req.body,{new:true});
    if(!updateJob){
      return res.status(404).json({ message: 'Job not found' });
    }
    res.json(updateJob);
  }
  catch(err){
    res.status(500).json({ message: 'Failed to update job', error: err.message });
  }
};

//delete job
exports.deleteJob = async(req,res,next)=>{
  try{
const deleteJob = await JobApplication.findOneAndDelete({_id:req.params.id,userId:req.user.id});
   if (!deleteJob) return res.status(404).json({ message: 'Job not found' });
    res.json({ message: 'Job deleted' });
  } catch (err) {
    res.status(500).json({ message: 'Failed to delete job', error: err.message });
  }
};
exports.matchResume = async (req,res,next)=>{
  try{
  const user = await User.findById(req.user.id);
  const job = await JobApplication.findById(req.params.jobId);

  const matched = user.resumeKeywords.filter(Kw=>job.keywords.includes(Kw));
   const missing = job.keywords.filter(kw => !matched.includes(kw));
    const score = job.keywords.length ? Math.round((matched.length / job.keywords.length) * 100) : 0;

    res.json({ matched, missing, score });
  }
  catch (err) {
    res.status(500).json({ error: 'Matching failed' });
  }
}

