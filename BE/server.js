const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// SQLite Database Connection
const dbPath = path.join(__dirname, '../youtube_links.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err);
  } else {
    console.log('Connected to SQLite database');
    initializeDatabase();
  }
});

// Initialize Database
function initializeDatabase() {
  db.run(`
    CREATE TABLE IF NOT EXISTS youtube_links (
      id TEXT PRIMARY KEY,
      videoId TEXT NOT NULL,
      youtubeLink TEXT NOT NULL,
      createdAt INTEGER NOT NULL,
      deleted INTEGER DEFAULT 0
    )
  `, (err) => {
    if (err) {
      console.error('Error creating table:', err);
    } else {
      console.log('Database table ready');
    }
  });
}

// API: GET /api/youtube-links
app.get('/api/youtube-links', (req, res) => {
  const sql = 'SELECT * FROM youtube_links ORDER BY createdAt DESC';
  
  db.all(sql, [], (err, rows) => {
    if (err) {
      console.error('Error fetching records:', err);
      res.status(500).json({ error: err.message });
    } else {
      res.json(rows);
    }
  });
});

// API: POST /api/update-deleted
app.post('/api/update-deleted', (req, res) => {
  const { ids, deleted } = req.body;

  if (!Array.isArray(ids) || ids.length === 0) {
    return res.status(400).json({ error: 'ids must be a non-empty array' });
  }

  if (typeof deleted !== 'number' || (deleted !== 0 && deleted !== 1)) {
    return res.status(400).json({ error: 'deleted must be 0 or 1' });
  }

  const placeholders = ids.map(() => '?').join(',');
  const sql = `UPDATE youtube_links SET deleted = ? WHERE id IN (${placeholders})`;
  const params = [deleted, ...ids];

  db.run(sql, params, (err) => {
    if (err) {
      console.error('Error updating records:', err);
      res.status(500).json({ error: err.message });
    } else {
      res.json({ message: 'Records updated successfully', changes: this.changes });
    }
  });
});

// Start Server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});

// Close DB on exit
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) console.error('Error closing database:', err);
    console.log('Database connection closed');
    process.exit(0);
  });
});
