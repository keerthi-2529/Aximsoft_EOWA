import os
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import query_db, execute_db

app = Flask(__name__)
app.secret_key = 'skillforge_super_secure_key_2026'


# Custom filter to split string (used in templates for curriculum topics)
@app.template_filter('split')
def split_filter(value, key=';'):
    return value.split(key) if value else []


# Decorator to secure routes requiring authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access that page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    """Renders the landing page with three featured courses."""
    courses = query_db("SELECT * FROM Courses LIMIT 3")
    return render_template('home.html', courses=courses)


@app.route('/courses')
def courses():
    """Renders the course catalog with search and category filtering."""
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    # Get all categories for filter dropdown options
    categories_row = query_db("SELECT DISTINCT category FROM Courses")
    categories = [r['category'] for r in categories_row]

    # Build query dynamically
    query = "SELECT * FROM Courses WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if category:
        query += " AND category = ?"
        params.append(category)

    courses_list = query_db(query, params)

    # Check current enrollments for logged in user to customize button displays
    enrolled_course_ids = {}
    if 'user_id' in session:
        enrollments = query_db("SELECT course_id, progress FROM Enrollments WHERE user_id = ?", (session['user_id'],))
        enrolled_course_ids = {e['course_id']: e['progress'] for e in enrollments}

    return render_template('courses.html', courses=courses_list, categories=categories,
                           enrolled_course_ids=enrolled_course_ids)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles logging in users and redirects to dashboard."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db("SELECT * FROM Users WHERE email = ?", (email,), one=True)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))

    return render_template('auth.html')


@app.route('/register', methods=['POST'])
def register():
    """Handles new user registrations, hashes passwords, and logs in user."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_pass = request.form.get('confirm_password', '')

    if not name or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for('login', tab='register'))

    if password != confirm_pass:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('login', tab='register'))

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for('login', tab='register'))

    # Check if user already exists
    existing = query_db("SELECT id FROM Users WHERE email = ?", (email,), one=True)
    if existing:
        flash("An account with that email already exists. Please sign in.", "warning")
        return redirect(url_for('login'))

    # Insert new user with hashed password
    hashed_pass = generate_password_hash(password)
    try:
        user_id = execute_db(
            "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_pass)
        )
        session['user_id'] = user_id
        session['user_name'] = name
        flash("Account successfully created! Welcome to SkillForge.", "success")
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash("An error occurred during registration. Please try again.", "danger")
        return redirect(url_for('login', tab='register'))


@app.route('/logout')
def logout():
    """Logs out user and clears the session."""
    session.clear()
    flash("You have successfully signed out.", "success")
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Renders user course learning list and computes completion statistics."""
    enrollments = query_db(
        """SELECT e.id,
                  e.progress,
                  e.enrollment_date,
                  e.certificate_id,
                  c.name,
                  c.category,
                  c.duration,
                  c.description,
                  c.image_url
           FROM Enrollments e
                    JOIN Courses c ON e.course_id = c.id
           WHERE e.user_id = ?
           ORDER BY e.enrollment_date DESC""",
        (session['user_id'],)
    )

    # Dashboard metrics calculation
    completed_count = sum(1 for e in enrollments if e['progress'] == 100)
    in_progress_count = sum(1 for e in enrollments if 0 < e['progress'] < 100)
    not_started_count = sum(1 for e in enrollments if e['progress'] == 0)

    total_progress = sum(e['progress'] for e in enrollments)
    avg_progress = round(total_progress / len(enrollments)) if enrollments else 0

    return render_template(
        'dashboard.html',
        enrollments=enrollments,
        completed_count=completed_count,
        in_progress_count=in_progress_count,
        not_started_count=not_started_count,
        avg_progress=avg_progress
    )


@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    """Enrolls the user in a course and initializes progress to 0%."""
    # Ensure they aren't already enrolled
    existing = query_db(
        "SELECT id FROM Enrollments WHERE user_id = ? AND course_id = ?",
        (session['user_id'], course_id),
        one=True
    )
    if existing:
        flash("You are already enrolled in this course.", "info")
        return redirect(url_for('dashboard'))

    try:
        execute_db(
            "INSERT INTO Enrollments (user_id, course_id) VALUES (?, ?)",
            (session['user_id'], course_id)
        )
        flash("Successfully enrolled! Let's start learning.", "success")
    except Exception as e:
        flash("Failed to enroll. Please try again.", "danger")

    return redirect(url_for('dashboard'))


@app.route('/update-progress/<int:enrollment_id>', methods=['POST'])
@login_required
def update_progress(enrollment_id):
    """Updates enrollment progress, handles certificate unlocking on 100% progress."""
    enrollment = query_db(
        "SELECT * FROM Enrollments WHERE id = ? AND user_id = ?",
        (enrollment_id, session['user_id']),
        one=True
    )
    if not enrollment:
        flash("Course enrollment record not found.", "danger")
        return redirect(url_for('dashboard'))

    try:
        progress = int(request.form.get('progress', 0))
        progress = max(0, min(100, progress))  # Clamp between 0 and 100

        if progress == 100:
            # Unlock certificate if not already unlocked
            certificate_id = enrollment['certificate_id']
            if not certificate_id:
                certificate_id = f"SF-{enrollment_id}-{uuid.uuid4().hex[:6].upper()}"

            completion_date = enrollment['completion_date'] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            execute_db(
                "UPDATE Enrollments SET progress = ?, certificate_id = ?, completion_date = ? WHERE id = ?",
                (progress, certificate_id, completion_date, enrollment_id)
            )
            flash("Congratulations! You completed the course and earned a certificate!", "success")
        else:
            # If progress falls below 100, invalidate certificate
            execute_db(
                "UPDATE Enrollments SET progress = ?, certificate_id = NULL, completion_date = NULL WHERE id = ?",
                (progress, enrollment_id)
            )
            flash("Course progress updated.", "success")

    except ValueError:
        flash("Invalid progress value submitted.", "danger")
    except Exception as e:
        flash("Failed to update course progress. Please try again.", "danger")

    return redirect(url_for('dashboard'))


@app.route('/certificate/<string:certificate_id>')
@login_required
def view_certificate(certificate_id):
    """Displays a printable completion certificate with secure verification attributes."""
    enrollment = query_db(
        """SELECT e.progress,
                  e.completion_date,
                  e.certificate_id,
                  u.name as user_name,
                  c.name,
                  c.category,
                  c.duration
           FROM Enrollments e
                    JOIN Users u ON e.user_id = u.id
                    JOIN Courses c ON e.course_id = c.id
           WHERE e.certificate_id = ?
             AND e.user_id = ?""",
        (certificate_id, session['user_id']),
        one=True
    )

    if not enrollment or enrollment['progress'] < 100:
        flash("Certificate not found or not yet unlocked.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('certificate.html', enrollment=enrollment)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Renders profile view or saves bio & name updates."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        bio = request.form.get('bio', '').strip()

        if not name:
            flash("Name field cannot be left blank.", "danger")
            return redirect(url_for('profile'))

        try:
            execute_db(
                "UPDATE Users SET name = ?, bio = ? WHERE id = ?",
                (name, bio, session['user_id'])
            )
            session['user_name'] = name
            flash("Profile changes saved successfully!", "success")
        except Exception as e:
            flash("Failed to update profile details. Please try again.", "danger")

        return redirect(url_for('profile'))

    user = query_db("SELECT * FROM Users WHERE id = ?", (session['user_id'],), one=True)

    enrollments = query_db(
        """SELECT e.progress, c.name, c.category, c.duration, c.description
           FROM Enrollments e
                    JOIN Courses c ON e.course_id = c.id
           WHERE e.user_id = ?
           ORDER BY e.enrollment_date DESC""",
        (session['user_id'],)
    )

    completed_count = sum(1 for e in enrollments if e['progress'] == 100)
    total_progress = sum(e['progress'] for e in enrollments)
    avg_progress = round(total_progress / len(enrollments)) if enrollments else 0

    return render_template(
        'profile.html',
        user=user,
        enrollments=enrollments,
        completed_count=completed_count,
        avg_progress=avg_progress
    )


def auto_init_database():
    """Checks if the database or Courses table is missing/empty, and automatically initializes and seeds them."""
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    db_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skillforge.db')

    db_exists = os.path.exists(db_file_path)
    needs_init = False

    if not db_exists:
        needs_init = True
    else:
        try:
            res = query_db("SELECT COUNT(*) as count FROM sqlite_master WHERE type='table' AND name='Courses'",
                           one=True)
            if not res or res['count'] == 0:
                needs_init = True
            else:
                courses_res = query_db("SELECT COUNT(*) as count FROM Courses", one=True)
                if not courses_res or courses_res['count'] == 0:
                    needs_init = True
        except Exception:
            needs_init = True

    if needs_init:
        print("Database missing or empty. Auto-initializing and seeding...")
        from database import init_db
        init_db(schema_path)

        # Seed courses
        from init_db import seed_courses
        seed_courses()


if __name__ == '__main__':
    # Auto-initialize database on startup
    auto_init_database()
    # Print launch confirmation
    print("Launching SkillForge Online Course Management System...")
    app.run(debug=True)