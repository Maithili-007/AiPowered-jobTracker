const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');

const getAuthResponse = (user) => {
  const token = jwt.sign(
    { id: user._id, email: user.email, name: user.name },
    process.env.JWT_SECRET,
    { expiresIn: '12h' }
  );

  return {
    token,
    user: { id: user._id, name: user.name, email: user.email },
  };
};

// Validation arrays
exports.signupValidators = [
   body('name').notEmpty().withMessage('Name is required'),//function that sets validation rules for a field in the (req.body).
  body('email').isEmail().withMessage('Invalid email'),
  body('password')
    .isLength({ min: 8 }).withMessage('Password must be at least 8 chars')
    .matches(/[A-Z]/)
  .withMessage("Password should contain atleast one uppercase letter")
  .matches(/[a-z]/)
  .withMessage("Password should contain atleast one lowercase letter")
  .matches(/[0-9]/)
  .withMessage("Password should contain atleast one number")
  .matches(/[!@&]/)
  .withMessage("Password should contain atleast one special character")
  .trim()
];

exports.loginValidators = [
  body('email').isEmail().withMessage('Invalid email'),
  body('password').exists().withMessage('Password is required')
];

// Handler functions
exports.postSignup = async (req, res) => {
  const errors = validationResult(req);//It is a function that checks if any of your validations failed.
  if (!errors.isEmpty())
    return res.status(400).json({ errors: errors.array() });

  const {name, email, password } = req.body;
  try {
    const exists = await User.findOne({ name });
    if (exists)
      return res.status(400).json({ message: 'User already exists' });

    const salt = await bcrypt.genSalt(10);
    const password_hash = await bcrypt.hash(password, salt);
    const user = await User.create({ name, email, password_hash });
    res.status(201).json({ user: { id: user._id, email: user.email, name:user.name } });
  } catch {
    res.status(500).json({ message: 'Signup failed' });
  }
};

exports.postLogin = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty())
    return res.status(400).json({ errors: errors.array() });//frontend receives property named "errors"

  const {  email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user)
      return res.status(401).json({ message: 'Invalid credentials' });
    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch)
      return res.status(401).json({ message: 'Invalid credentials' });

    res.json(getAuthResponse(user));
  } catch {
    res.status(500).json({ message: 'Login failed' });
  }
};

exports.postDemoLogin = async (req, res) => {
  const demoEmail = process.env.DEMO_LOGIN_EMAIL;

  if (!demoEmail) {
    return res.status(500).json({ message: 'Demo login is not configured' });
  }

  try {
    const user = await User.findOne({ email: demoEmail });
    if (!user) {
      return res.status(404).json({ message: 'Demo user not found' });
    }

    return res.json(getAuthResponse(user));
  } catch {
    return res.status(500).json({ message: 'Demo login failed' });
  }
};
