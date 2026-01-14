Fake News Detection Web App

Overview
This project is a Fake News Detection Web Application built using Flask. The app allows users to register with their name and phone number, submit news articles (titles and/or text), and receive instant verification results. It combines Google Fact Check API and a custom rule-based fake news detector to evaluate news credibility.

Features

User Registration & Login
Users can securely register using their name and phone number. Sessions are managed to maintain user login state.

News Detection

Submit a news title, text, and optionally the source.

The app first checks the news using Google Fact Check API.

If Google does not provide a verdict, a rule-based fake news detection algorithm analyzes the content.

Results include a fake/real/suspicious verdict, confidence level, score, and reasons for the decision.

Recent detection results from Google (if available) are also displayed.

History Tracking
The app saves all detection results in a CSV file. Users can view the last 10 detection results.

Statistics
Users can view aggregated statistics, including:

Total news checked

Number of fake news

Number of real news

Number of suspicious news

Secure Session Management
User sessions are handled using Flask sessions with a secret key to protect data integrity.

Data Persistence

User registration info stored in data/users.csv

Detection results stored in data/detection_history.csv

Tech Stack

Backend: Python, Flask

Frontend: HTML, CSS, JavaScript

Data Storage: CSV files (for simplicity)

APIs: Google Fact Check API

Custom Logic: Rule-based fake news detection

Project Structure
app.py                  # Main Flask application
templates/              # HTML templates (login, home, history, stats)
static/                 # CSS, JS, and images
data/
  users.csv             # Stores registered user info
  detection_history.csv # Stores news detection results
google_checker.py       # Integration with Google Fact Check API
rule_detector.py        # Custom fake news detection rules

Usage

Clone the repository:

git clone https://github.com/yourusername/fake-news-detection.git


Install dependencies:

pip install flask requests


Run the application:

python app.py


Access the app in your browser at: http://localhost:5000

Register, submit news, and explore history & statistics.

Notes

The project currently uses CSV files for storage; it can be upgraded to use databases like MySQL or PostgreSQL.

Google Fact Check integration requires API access.

The rule-based detection logic can be customized or enhanced with machine learning models in the future.
