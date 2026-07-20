import os
import sqlite3
from datetime import datetime

from flask import g
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "jobportal.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")


# ----------------------------------------------------------------------------
# Connection handling
# ----------------------------------------------------------------------------
def get_db():
    """Return a SQLite connection stored on Flask's application context (g)."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register database lifecycle hooks on the Flask app."""
    app.teardown_appcontext(close_db)


# ----------------------------------------------------------------------------
# Schema initialization
# ----------------------------------------------------------------------------
def init_db():
    """Create tables from schema.sql (if they don't already exist)."""
    db = sqlite3.connect(DATABASE)
    with open(SCHEMA_FILE, "r") as f:
        db.executescript(f.read())
    db.commit()

    cur = db.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        seed_sample_data(db)

    db.close()


# ----------------------------------------------------------------------------
# Notification helper
# ----------------------------------------------------------------------------
def create_notification(db, user_id, message, link=None):
    """Insert a notification for a given user and commit immediately."""
    db.execute(
        "INSERT INTO notifications (user_id, message, link, is_read, created_at) "
        "VALUES (?,?,?,0,?)",
        (user_id, message, link, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    db.commit()


# ----------------------------------------------------------------------------
# Sample data seeding
# ----------------------------------------------------------------------------
def seed_sample_data(db):
    now = datetime.now().strftime("%Y-%m-%d")
    employers = [
        ("Aarav Mehta", "hr@technova.com", "TechNova Solutions"),
        ("Priya Nair", "careers@brightfin.com", "BrightFin Capital"),
        ("Rohit Sharma", "jobs@pixeldesign.com", "Pixel Design Studio"),
    ]
    employer_ids = []
    for name, email, company in employers:
        cur = db.execute(
            "INSERT INTO users (name, email, password, role, company_name, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (name, email, generate_password_hash("password123"), "employer", company, now),
        )
        employer_ids.append(cur.lastrowid)

    db.execute(
        "INSERT INTO users (name, email, password, role, skills, experience, created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        ("Demo Candidate", "candidate@example.com", generate_password_hash("password123"),
         "candidate", "Python, Flask, SQL", "1 year", now),
    )

    jobs = [
        (employer_ids[0], "TechNova Solutions", "Python Backend Developer", "Bengaluru, India",
         "Full-time", "1-3 years", "₹6,00,000 - ₹9,00,000", "Python, Flask, SQL, REST APIs",
         "We are looking for a Python developer to build and maintain scalable backend services "
         "using Flask and SQL databases. You will work closely with the product team."),
        (employer_ids[0], "TechNova Solutions", "Frontend Developer (React)", "Remote",
         "Remote", "0-2 years", "₹5,00,000 - ₹8,00,000", "React, JavaScript, CSS, Bootstrap",
         "Build responsive and elegant user interfaces for our SaaS products using React and "
         "modern CSS frameworks."),
        (employer_ids[1], "BrightFin Capital", "Financial Analyst", "Mumbai, India",
         "Full-time", "2-4 years", "₹7,00,000 - ₹10,00,000", "Excel, Financial Modeling, SQL",
         "Analyze financial data, build models and support investment decisions for our "
         "growing portfolio."),
        (employer_ids[1], "BrightFin Capital", "Finance Intern", "Mumbai, India",
         "Internship", "0-1 years", "₹15,000/month", "Excel, Communication",
         "Great opportunity for finance students to gain hands-on experience in a fast paced "
         "financial firm."),
        (employer_ids[2], "Pixel Design Studio", "UI/UX Designer", "Pune, India",
         "Full-time", "1-3 years", "₹5,00,000 - ₹7,50,000", "Figma, Adobe XD, Prototyping",
         "Design delightful user experiences for web and mobile applications for our clients "
         "across industries."),
        (employer_ids[2], "Pixel Design Studio", "Graphic Design Intern", "Remote",
         "Internship", "0-1 years", "₹10,000/month", "Photoshop, Illustrator",
         "Assist the design team in creating marketing collateral, social media creatives and "
         "branding assets."),
    ]
    for j in jobs:
        db.execute(
            "INSERT INTO jobs (employer_id, company_name, job_title, location, job_type, "
            "experience, salary, skills, description, posted_date) VALUES (?,?,?,?,?,?,?,?,?,?)",
            j + (now,),
        )
    db.commit()


if __name__ == "__main__":
    # Allows running `python database.py` directly to (re)initialize the DB.
    init_db()
    print(f"Database initialized at {DATABASE}")
