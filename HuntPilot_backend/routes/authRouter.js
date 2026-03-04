const express = require('express');
const authRouter = express.Router();
const authController = require('../controllers/authController');


authRouter.post('/signup', authController.signupValidators, authController.postSignup);
authRouter.post('/login', authController.loginValidators, authController.postLogin);
authRouter.post('/demo-login', authController.postDemoLogin);

module.exports = authRouter;
