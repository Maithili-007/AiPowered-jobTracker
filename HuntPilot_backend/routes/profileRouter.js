const express = require('express');
const profileRouter = express.Router();
const profileController = require('../controllers/profileController');
const auth = require('../middleware/auth');
const multer = require('multer');
const upload = multer({dest:'uploads/'});//temporarily store uploaded files

profileRouter.post('/upload-resume', auth, upload.single('resume'),profileController.uploadResume);
profileRouter.get('/resume',  auth,profileController.getResume);
profileRouter.delete('/resume', auth, profileController.deleteResume);
profileRouter.get('/resume/download', auth,profileController.downloadResume);


module.exports = profileRouter;
