const express = require("express");
const helmet = require("helmet");
const cors = require("cors");
const auth = require("./middlewares/auth");

const app = express();

// Middlewares
app.use(helmet());
app.use(cors({ origin: ["http://localhost:3000", "https://your-app.com"] }));
app.use(express.json());

// Routes
app.use("/api/auth", require("./routes/auth"));
app.use("/api/protected", auth, require("./routes/protected")); // 👈 Auth required
