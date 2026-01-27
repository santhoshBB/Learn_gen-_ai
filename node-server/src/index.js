require("dotenv").config();
const express = require("express");
const { Pool } = require("pg");

const app = express();
app.use(express.json());

// PostgreSQL connection pool
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

// Health check (optional)
app.get("/health", (_, res) => {
  res.json({ status: "ok" });
});

// LOGIN ROUTE
app.post("/login", async (req, res) => {
  const { mobile } = req.body;

  if (!mobile) {
    return res.status(400).json({ message: "Mobile number required" });
  }

  try {
    const query = `
      SELECT id, mobile, "name"
      FROM public."user"
      WHERE mobile = $1
    `;

    const { rows } = await pool.query(query, [mobile]);

    if (rows.length === 0) {
      return res.status(401).json({ success:false,message: "Unauthorized" });
    }

    // User found
    return res.json({
      success: true,
      user: rows[0],
    });

  } catch (err) {
    console.error("DB error:", err);
    return res.status(500).json({ message: "Internal server error" });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Express server running on port ${PORT}`);
});
