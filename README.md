<<<<<<< HEAD
# AI Digital Carbon Tracker

A full-stack digital carbon footprint tracker built with Python Flask, MySQL, Chart.js, and modern glassmorphism UI.

## Features

- Login / Register authentication with Flask and MySQL
- Animated modern UI with dark/light theme toggle
- Dashboard with daily, weekly, and monthly carbon totals
- App usage input for Instagram, WhatsApp, YouTube, Netflix, Gmail, Google Drive, Spotify, and Zoom
- Dynamic Chart.js charts and eco tips
- Browser notifications for high usage thresholds
- PDF download report generation
- Leaderboard for eco leaders
- Responsive mobile-friendly layout

## Setup Instructions

1. Install Python 3.11+ and XAMPP with MySQL.
2. Start Apache and MySQL from XAMPP.
3. Create the database using the SQL schema:
   - Open `phpMyAdmin` or MySQL CLI
   - Run the statements in `schema.sql`
4. Install Python dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Update database credentials in `app.py` if needed:
   ```python
   app.config['MYSQL_USER'] = 'root'
   app.config['MYSQL_PASSWORD'] = ''
   app.config['MYSQL_DB'] = 'digital_carbon_tracker'
   ```
6. Run the Flask app:
   ```powershell
   python app.py
   ```
7. Open a browser and visit `http://127.0.0.1:5000`

## Notes

- Use the login/register pages to create a new user.
- Dashboard offers a full usage input experience with charts, suggestions, and notifications.
- The `download-report` endpoint generates a PDF summary of your latest report.

## Recommended Improvements

- Replace `app.secret_key` with a secure random value for production.
- Set `debug=False` when deploying.
=======
# digital-carbon-tracker
AI-powered Digital Carbon Tracker web application built using Flask, MySQL, HTML, CSS, and JavaScript. The project tracks app usage, calculates carbon footprint, generates eco alerts, dynamic green scores, leaderboards, and promotes sustainable digital habits through an interactive dashboard.
>>>>>>> 8077462c21f521788afad043c0c47001f96c545c
