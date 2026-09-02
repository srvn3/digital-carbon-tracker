# AI Digital Carbon Tracker

A full-stack web application that helps users understand the environmental impact of their digital habits. The system tracks usage across commonly used applications, estimates the associated digital carbon footprint, and presents the results through an interactive dashboard.

## Features

* User registration and login
* Digital usage tracking for applications such as YouTube, Instagram, WhatsApp, Netflix, Spotify, Gmail, Google Drive and Zoom
* Daily, weekly and monthly carbon footprint summaries
* Interactive charts using Chart.js
* Green score and eco-friendly suggestions
* Usage-based eco alerts and browser notifications
* Eco leaderboard
* PDF report generation
* Responsive dashboard with dark/light theme

## Tech Stack

* **Frontend:** HTML, CSS, JavaScript, Chart.js
* **Backend:** Python, Flask
* **Database:** MySQL
* **Authentication:** Flask-based authentication
* **Reports:** PDF generation

## How It Works

Users enter their digital application usage, after which the system calculates an estimated carbon footprint based on the recorded usage. The dashboard presents the results through charts, scores and recommendations to help users become more aware of their digital habits.

## Running Locally

### Requirements

* Python 3.11+
* XAMPP with MySQL
* A web browser

### Setup

1. Clone the repository.

2. Create the MySQL database using `schema.sql`.

3. Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

4. Configure the database credentials in `app.py` or through environment variables.

5. Start MySQL using XAMPP.

6. Run the Flask application:

```bash
python app.py
```

7. Open:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
digital-carbon-tracker/
├── static/
├── templates/
├── app.py
├── schema.sql
├── requirements.txt
├── setup_oauth.py
└── README.md
```

## Project Purpose

The project explores how everyday digital activity can be made more visible from an environmental perspective, while encouraging users to adopt more sustainable digital habits.
