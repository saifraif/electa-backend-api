const router = require("express").Router();
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

// Mock user database (replace with real DB)
const users = [
  {
    id: 1,
    email: "admin@electa.com",
    password: bcrypt.hashSync("securepassword", 10),
  },
];

router.post("/login", (req, res) => {
  // 1. Find user
  const user = users.find((u) => u.email === req.body.email);
  if (!user) return res.status(404).json({ error: "User not found" });

  // 2. Validate password
  const validPass = bcrypt.compareSync(req.body.password, user.password);
  if (!validPass) return res.status(400).json({ error: "Invalid password" });

  // 3. Generate token
  const token = jwt.sign(
    { id: user.id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: process.env.TOKEN_EXPIRES_IN }
  );

  // 4. Send token (HTTP-only cookie + response)
  res.cookie("token", token, { httpOnly: true, secure: true });
  res.json({ token });
});

module.exports = router;
