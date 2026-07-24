💼 Job Portal Web Application
A modern Job Portal Web Application developed using Flask, SQLite, HTML, CSS, and Bootstrap. The application enables employers to post job openings and job seekers to browse and search available jobs through an intuitive web interface.

📌 Features
Home Page
Attractive landing page
Latest job listings
Platform statistics
Responsive navigation bar
Job Listings
View all available jobs
Search jobs by title, company, or location
Filter job listings
View detailed job descriptions
Employer Features
Add new job postings
Update existing job postings
Delete job postings
Manage job information
User Authentication
User registration
Secure login
Session management
Logout functionality
Dashboard
Personalized dashboard
Quick access to job management
User profile information
Database Management
SQLite database
Automatic database initialization
CRUD operations
Schema-based table creation
🛠️ Technologies Used
Backend
Python
Flask
SQLite3
Frontend
HTML5
CSS3
Bootstrap 5
Jinja2 Templates
Libraries
Flask
sqlite3
os
uuid
datetime
werkzeug.security
📂 Project Structure
JobPortal/
│
├── app.py
├── database.py
├── schema.sql
├── jobportal.db
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── jobs.html
│   ├── job_detail.html
│   ├── dashboard.html
│   ├── auth.html
│   ├── post_job.html
│   ├── edit_job.html
│   └── profile.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│
└── README.md
⚙️ Installation
1. Clone the Repository
git clone https://github.com/yourusername/job-portal.git
2. Navigate to Project Folder
cd job-portal
3. Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Linux/Mac
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
pip install flask
or

pip install -r requirements.txt
5. Run the Application
python app.py
Open your browser and visit

http://127.0.0.1:5000/
🗄️ Database
The application uses SQLite.

Database files:

jobportal.db
schema.sql
The database is automatically initialized using the schema file if it does not already exist.

📸 Screenshots
Add screenshots of:

Home Page
Login Page
Register Page
Dashboard
Job Listings
Job Details
Post Job Page
📖 How the Application Works
User opens the home page.
New users register an account.
Existing users log in securely.
Employers can post new jobs.
Job seekers browse available jobs.
Users can search for jobs by title, company, or location.
Employers can edit or delete their job postings.
All data is stored in an SQLite database.
🔒 Security Features
Password hashing using Werkzeug
Session-based authentication
Protected routes
Input validation
Flash messages for user feedback
🚀 Future Enhancements
Resume upload
Job application tracking
Email notifications
Company profiles
Admin panel
Advanced search filters
Pagination
REST API integration
Cloud database support
🎯 Learning Outcomes
This project demonstrates:

Flask web development
CRUD operations
SQLite database integration
User authentication
Session management
Template inheritance using Jinja2
Responsive UI development
MVC architecture
Form handling
Database schema management
👨‍💻 Author
Keerthi

Python Developer | Flask Developer | Aspiring Data Scientist

📜 License
This project is developed for educational purposes and can be freely modified and used for learning.
