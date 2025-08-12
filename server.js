const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the "public" folder (adjust if needed)
app.use(express.static(path.join(__dirname, 'public')));

// Fallback for SPA routing (optional)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
