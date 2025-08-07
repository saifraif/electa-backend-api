const jwt = require("jsonwebtoken");

module.exports = (req, res, next) => {
  // 1. Get token from header
  const token = req.header("x-auth-token") || req.cookies.token;

  // 2. Reject if no token
  if (!token) return res.status(401).json({ error: "Access denied" });

  // 3. Verify token
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // Attach user to request
    next();
  } catch (err) {
    res.status(400).json({ error: "Invalid token" });
  }
};
