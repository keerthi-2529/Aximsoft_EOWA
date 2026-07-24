SkillForge – E-Learning Platform
Project Overview
SkillForge is a Flask-based E-Learning Platform that enables users to browse courses, enroll in programs, monitor learning progress, and earn certificates upon course completion. The platform provides a modern, responsive interface and stores data using SQLite.

Features
User Registration and Login
Secure Password Authentication
Course Catalog
Course Enrollment
Student Dashboard
Progress Tracking
Certificate Generation
User Profile Management
Responsive User Interface
Flash Messages and Form Validation
Technologies Used
Frontend
HTML5
CSS3
Bootstrap 5
Bootstrap Icons
Jinja2 Templates
Backend
Python
Flask
Database
SQLite
Libraries
Werkzeug
Jinja2
Project Structure
SkillForge/
│
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   └── main.js (or embedded in base.html)
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── courses.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── login.html
│   ├── certificate.html
│   └── ...
│
├── app.py
├── database.py
├── init_db.py
├── schema.sql
├── skillforge.db
└── README.md
Installation
Clone the Repository
git clone https://github.com/yourusername/SkillForge.git
Move into Project Folder
cd SkillForge
Install Required Packages
pip install flask werkzeug
Database Setup
Initialize the database by running:

python init_db.py
This will:

Create the SQLite database
Create all required tables
Seed sample courses
Run the Project
python app.py
Open your browser and visit:

http://127.0.0.1:5000
Modules
Home
Displays

Hero Section
Featured Courses
Statistics
Platform Features
Authentication
User Registration
User Login
Password Security
Courses
Users can

Browse Courses
View Course Details
Enroll in Courses
Dashboard
Displays

Enrolled Courses
Progress
Completion Status
Certificates
Profile
Allows users to

View Personal Information
Manage Account
Database Tables
Users
id
name
email
password
Courses
id
name
category
duration
description
image_url
syllabus
Enrollments
id
user_id
course_id
progress
status
Screenshots
Home Page
Course Catalog
Login Page
Dashboard
Profile
Certificate Page
(Add screenshots here.)

Future Enhancements
Instructor Dashboard
Online Quiz Module
Video Streaming
Payment Gateway
Discussion Forum
Email Notifications
Search and Filter
Dark Mode
Mobile App Integration
Learning Outcomes
This project demonstrates:

Flask Web Development
SQLite Database Management
User Authentication
CRUD Operations
Jinja2 Template Engine
Responsive Web Design
Session Management
MVC Architecture
Author
Keerthi

Python Developer | Flask Developer | Web Developer

License
This project is developed for educational purposes.
