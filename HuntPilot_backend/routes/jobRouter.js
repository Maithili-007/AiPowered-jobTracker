const express = require('express');
const jobRouter = express.Router();
const jobController = require('../controllers/jobController');
const auth = require('../middleware/auth');

jobRouter.get('/',auth, jobController.getJobs);//If the auth middleware doesn't work, then the route will never reach jobController.getJobs
jobRouter.post('/',auth, jobController.createJob);
jobRouter.post('/:jobId/match-profile',auth, jobController.matchResume);
jobRouter.get('/:id',auth, jobController.getJobById);
jobRouter.put('/:id',auth, jobController.updateJob);
jobRouter.delete('/:id',auth, jobController.deleteJob);


module.exports = jobRouter;
