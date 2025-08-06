const jwt = require('jsonwebtoken');//to identify user, without needing to store session data on the server.

function auth(req, res, next) {
  const token = req.headers.authorization;
  if (!token) return res.status(401).json({ message: 'No token provided' });
  try {
    const decoded = jwt.verify(token.replace('Bearer ', ''), process.env.JWT_SECRET);// to check if token is valid, returns the decoded payload that you originally used when creating the token.
    req.user = decoded;
    next();//go to the controller function if token verified
  } catch {
    res.status(401).json({ message: 'Invalid token' });
  }
}
module.exports = auth;
