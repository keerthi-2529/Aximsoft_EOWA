import os
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                    session, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import database as db_module
from database import get_db, create_notification

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, "profiles")
ALLOWED_RESUME_EXT = {"pdf", "doc", "docx"}
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Register database teardown hook with the Flask app
db_module.init_app(app)

JOB_TYPES = ["Full-time", "Part-time", "Internship", "Contract", "Remote"]

# Manually selectable statuses (an employer sets these from a dropdown).
# "Interview Scheduled" is set automatically via the Schedule Interview action.
STATUS_LIST = ["Applied", "Under Review", "Shortlisted", "Rejected"]

STATUS_BADGE = {
    "Applied": "secondary",
    "Under Review": "info",
    "Shortlisted": "primary",
    "Interview Scheduled": "warning",
    "Rejected": "danger",
}
JOB_CATEGORY_ICONS = [
    ("Technology", "bi-laptop"),
    ("Marketing", "bi-megaphone"),
    ("Finance", "bi-cash-coin"),
    ("Design", "bi-palette"),
    ("Sales", "bi-graph-up-arrow"),
    ("Human Resources", "bi-people"),
]


# ----------------------------------------------------------------------------
# Helpers / decorators
# ----------------------------------------------------------------------------
def allowed_file(filename, allowed_ext):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_ext


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if session.get("role") != role:
                flash("You don't have permission to access that page.", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


def current_user():
    if "user_id" not in session:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


@app.context_processor
def inject_globals():
    unread_count = 0
    recent_notifications = []
    if "user_id" in session:
        db = get_db()
        unread_count = db.execute(
            "SELECT COUNT(*) c FROM notifications WHERE user_id = ? AND is_read = 0",
            (session["user_id"],),
        ).fetchone()["c"]
        recent_notifications = db.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (session["user_id"],),
        ).fetchall()
    return {
        "current_user": current_user(),
        "STATUS_BADGE": STATUS_BADGE,
        "unread_count": unread_count,
        "recent_notifications": recent_notifications,
    }


# ----------------------------------------------------------------------------
# Public routes
# ----------------------------------------------------------------------------
@app.route("/")
def home():
    db = get_db()
    latest_jobs = db.execute(
        "SELECT * FROM jobs ORDER BY id DESC LIMIT 6"
    ).fetchall()
    stats = {
        "jobs": db.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"],
        "companies": db.execute(
            "SELECT COUNT(DISTINCT company_name) c FROM jobs").fetchone()["c"],
        "candidates": db.execute(
            "SELECT COUNT(*) c FROM users WHERE role='candidate'").fetchone()["c"],
    }
    companies = db.execute(
        "SELECT DISTINCT company_name FROM jobs"
    ).fetchall()
    return render_template(
        "index.html", jobs=latest_jobs, stats=stats, companies=companies,
        categories=JOB_CATEGORY_ICONS,
    )


@app.route("/jobs")
def jobs():
    db = get_db()
    query = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()
    experience = request.args.get("experience", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 6

    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if query:
        sql += " AND (job_title LIKE ? OR company_name LIKE ? OR skills LIKE ?)"
        like = f"%{query}%"
        params += [like, like, like]
    if location:
        sql += " AND location LIKE ?"
        params.append(f"%{location}%")
    if job_type:
        sql += " AND job_type = ?"
        params.append(job_type)
    if experience:
        sql += " AND experience LIKE ?"
        params.append(f"%{experience}%")

    count_sql = sql.replace("SELECT *", "SELECT COUNT(*) c")
    total = db.execute(count_sql, params).fetchone()["c"]
    total_pages = max((total + per_page - 1) // per_page, 1)
    page = min(page, total_pages)

    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params += [per_page, (page - 1) * per_page]
    job_rows = db.execute(sql, params).fetchall()

    saved_ids = set()
    if session.get("user_id") and session.get("role") == "candidate":
        rows = db.execute(
            "SELECT job_id FROM saved_jobs WHERE user_id = ?", (session["user_id"],)
        ).fetchall()
        saved_ids = {r["job_id"] for r in rows}

    return render_template(
        "jobs.html", jobs=job_rows, job_types=JOB_TYPES, query=query,
        location=location, job_type=job_type, experience=experience,
        page=page, total_pages=total_pages, saved_ids=saved_ids,
    )


@app.route("/jobs/<int:job_id>")
def job_details(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        abort(404)
    already_applied = False
    if session.get("user_id") and session.get("role") == "candidate":
        row = db.execute(
            "SELECT id FROM applications WHERE user_id = ? AND job_id = ?",
            (session["user_id"], job_id),
        ).fetchone()
        already_applied = row is not None
    related = db.execute(
        "SELECT * FROM jobs WHERE company_name = ? AND id != ? LIMIT 3",
        (job["company_name"], job_id),
    ).fetchall()
    return render_template(
        "job_details.html", job=job, already_applied=already_applied, related=related
    )


# ----------------------------------------------------------------------------
# Auth routes
# ----------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        role = request.form.get("role", "candidate")
        company_name = request.form.get("company_name", "").strip()
        resume = request.files.get("resume")

        errors = []
        if not name or not email or not password:
            errors.append("Please fill in all required fields.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if role == "employer" and not company_name:
            errors.append("Company name is required for employer accounts.")
        if role == "candidate":
            if not resume or not resume.filename:
                errors.append("Please upload your resume to register as a candidate.")
            elif not allowed_file(resume.filename, ALLOWED_RESUME_EXT):
                errors.append("Resume must be a PDF, DOC, or DOCX file.")

        db = get_db()
        if not errors:
            existing = db.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html", form=request.form)

        cur = db.execute(
            "INSERT INTO users (name, email, password, role, company_name, created_at) "
            "VALUES (?,?,?,?,?,?)",
            (name, email, generate_password_hash(password), role, company_name,
             datetime.now().strftime("%Y-%m-%d")),
        )
        db.commit()
        new_user_id = cur.lastrowid

        if role == "candidate" and resume and resume.filename:
            os.makedirs(RESUME_FOLDER, exist_ok=True)
            resume_filename = secure_filename(f"user{new_user_id}_{resume.filename}")
            resume.save(os.path.join(RESUME_FOLDER, resume_filename))
            db.execute(
                "UPDATE users SET resume_file = ? WHERE id = ?", (resume_filename, new_user_id)
            )
            db.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            if user["role"] == "employer":
                return redirect(url_for("employer_dashboard"))
            return redirect(url_for("candidate_dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ----------------------------------------------------------------------------
# Candidate routes
# ----------------------------------------------------------------------------
@app.route("/apply/<int:job_id>", methods=["POST"])
@role_required("candidate")
def apply_job(job_id):
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        abort(404)

    existing = db.execute(
        "SELECT id FROM applications WHERE user_id = ? AND job_id = ?",
        (session["user_id"], job_id),
    ).fetchone()
    if existing:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("job_details", job_id=job_id))

    user = current_user()
    if not user["resume_file"]:
        flash("Please upload your resume in your profile before applying.", "danger")
        return redirect(url_for("profile"))

    db.execute(
        "INSERT INTO applications (user_id, job_id, resume_file, applied_date, status) "
        "VALUES (?,?,?,?,?)",
        (session["user_id"], job_id, user["resume_file"],
         datetime.now().strftime("%Y-%m-%d"), "Applied"),
    )
    db.commit()

    create_notification(
        db, job["employer_id"],
        f"{user['name']} applied for '{job['job_title']}'",
        url_for("view_applicants", job_id=job_id),
    )

    flash("Application submitted successfully!", "success")
    return redirect(url_for("candidate_dashboard"))


@app.route("/save/<int:job_id>", methods=["POST"])
@role_required("candidate")
def save_job(job_id):
    db = get_db()
    existing = db.execute(
        "SELECT id FROM saved_jobs WHERE user_id = ? AND job_id = ?",
        (session["user_id"], job_id),
    ).fetchone()
    if existing:
        db.execute("DELETE FROM saved_jobs WHERE id = ?", (existing["id"],))
        flash("Job removed from saved list.", "info")
    else:
        db.execute(
            "INSERT INTO saved_jobs (user_id, job_id, saved_date) VALUES (?,?,?)",
            (session["user_id"], job_id, datetime.now().strftime("%Y-%m-%d")),
        )
        flash("Job saved successfully!", "success")
    db.commit()
    return redirect(request.referrer or url_for("jobs"))


@app.route("/dashboard/candidate")
@role_required("candidate")
def candidate_dashboard():
    db = get_db()
    applications = db.execute(
        "SELECT a.*, j.job_title, j.company_name, j.location "
        "FROM applications a JOIN jobs j ON a.job_id = j.id "
        "WHERE a.user_id = ? ORDER BY a.id DESC",
        (session["user_id"],),
    ).fetchall()
    saved = db.execute(
        "SELECT j.* FROM saved_jobs s JOIN jobs j ON s.job_id = j.id "
        "WHERE s.user_id = ? ORDER BY s.id DESC",
        (session["user_id"],),
    ).fetchall()
    summary = {
        "total_applied": len(applications),
        "shortlisted": sum(1 for a in applications if a["status"] == "Shortlisted"),
        "interviews": sum(1 for a in applications if a["status"] == "Interview Scheduled"),
        "saved": len(saved),
    }
    return render_template(
        "candidate_dashboard.html", applications=applications, saved=saved, summary=summary
    )


# ----------------------------------------------------------------------------
# Employer routes
# ----------------------------------------------------------------------------
@app.route("/dashboard/employer")
@role_required("employer")
def employer_dashboard():
    db = get_db()
    my_jobs = db.execute(
        "SELECT * FROM jobs WHERE employer_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()
    job_ids = [j["id"] for j in my_jobs]
    total_applicants = 0
    if job_ids:
        placeholders = ",".join("?" * len(job_ids))
        total_applicants = db.execute(
            f"SELECT COUNT(*) c FROM applications WHERE job_id IN ({placeholders})",
            job_ids,
        ).fetchone()["c"]
    summary = {
        "total_jobs": len(my_jobs),
        "total_applicants": total_applicants,
    }
    return render_template("employer_dashboard.html", jobs=my_jobs, summary=summary)


@app.route("/jobs/post", methods=["GET", "POST"])
@role_required("employer")
def post_job():
    if request.method == "POST":
        user = current_user()
        job_title = request.form.get("job_title", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "")
        experience = request.form.get("experience", "").strip()
        salary = request.form.get("salary", "").strip()
        skills = request.form.get("skills", "").strip()
        description = request.form.get("description", "").strip()
        company_name = request.form.get("company_name", user["company_name"] or "").strip()

        if not all([job_title, location, job_type, description]):
            flash("Please fill in all required fields.", "danger")
            return render_template("post_job.html", job_types=JOB_TYPES, form=request.form)

        db = get_db()
        db.execute(
            "INSERT INTO jobs (employer_id, company_name, job_title, location, job_type, "
            "experience, salary, skills, description, posted_date) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (session["user_id"], company_name, job_title, location, job_type, experience,
             salary, skills, description, datetime.now().strftime("%Y-%m-%d")),
        )
        db.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for("employer_dashboard"))

    return render_template("post_job.html", job_types=JOB_TYPES, form={})


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@role_required("employer")
def edit_job(job_id):
    db = get_db()
    job = db.execute(
        "SELECT * FROM jobs WHERE id = ? AND employer_id = ?",
        (job_id, session["user_id"]),
    ).fetchone()
    if not job:
        abort(404)

    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "")
        experience = request.form.get("experience", "").strip()
        salary = request.form.get("salary", "").strip()
        skills = request.form.get("skills", "").strip()
        description = request.form.get("description", "").strip()
        company_name = request.form.get("company_name", "").strip()

        if not all([job_title, location, job_type, description]):
            flash("Please fill in all required fields.", "danger")
            return render_template("edit_job.html", job=job, job_types=JOB_TYPES)

        db.execute(
            "UPDATE jobs SET company_name=?, job_title=?, location=?, job_type=?, "
            "experience=?, salary=?, skills=?, description=? WHERE id=?",
            (company_name, job_title, location, job_type, experience, salary, skills,
             description, job_id),
        )
        db.commit()
        flash("Job updated successfully!", "success")
        return redirect(url_for("employer_dashboard"))

    return render_template("edit_job.html", job=job, job_types=JOB_TYPES)


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
@role_required("employer")
def delete_job(job_id):
    db = get_db()
    job = db.execute(
        "SELECT * FROM jobs WHERE id = ? AND employer_id = ?",
        (job_id, session["user_id"]),
    ).fetchone()
    if not job:
        abort(404)
    db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    db.commit()
    flash("Job deleted successfully.", "info")
    return redirect(url_for("employer_dashboard"))


@app.route("/jobs/<int:job_id>/applicants")
@role_required("employer")
def view_applicants(job_id):
    db = get_db()
    job = db.execute(
        "SELECT * FROM jobs WHERE id = ? AND employer_id = ?",
        (job_id, session["user_id"]),
    ).fetchone()
    if not job:
        abort(404)
    applicants = db.execute(
        "SELECT a.*, u.name, u.email, u.phone, u.skills AS candidate_skills, "
        "u.experience AS candidate_experience "
        "FROM applications a JOIN users u ON a.user_id = u.id "
        "WHERE a.job_id = ? ORDER BY a.id DESC",
        (job_id,),
    ).fetchall()
    return render_template(
        "applicants.html", job=job, applicants=applicants, status_list=STATUS_LIST
    )


@app.route("/applications/<int:app_id>/status", methods=["POST"])
@role_required("employer")
def update_status(app_id):
    db = get_db()
    application = db.execute(
        "SELECT a.*, j.employer_id, j.id as job_id, j.job_title FROM applications a "
        "JOIN jobs j ON a.job_id = j.id WHERE a.id = ?",
        (app_id,),
    ).fetchone()
    if not application or application["employer_id"] != session["user_id"]:
        abort(404)
    new_status = request.form.get("status")
    if new_status in STATUS_LIST:
        db.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
        db.commit()
        create_notification(
            db, application["user_id"],
            f"Your application for '{application['job_title']}' is now '{new_status}'",
            url_for("candidate_dashboard"),
        )
        flash("Application status updated.", "success")
    return redirect(url_for("view_applicants", job_id=application["job_id"]))


@app.route("/applications/<int:app_id>/schedule", methods=["POST"])
@role_required("employer")
def schedule_interview(app_id):
    db = get_db()
    application = db.execute(
        "SELECT a.*, j.employer_id, j.id as job_id, j.job_title FROM applications a "
        "JOIN jobs j ON a.job_id = j.id WHERE a.id = ?",
        (app_id,),
    ).fetchone()
    if not application or application["employer_id"] != session["user_id"]:
        abort(404)

    interview_datetime = request.form.get("interview_datetime", "").strip()
    interview_location = request.form.get("interview_location", "").strip()

    if not interview_datetime:
        flash("Please select an interview date and time.", "danger")
        return redirect(url_for("view_applicants", job_id=application["job_id"]))

    db.execute(
        "UPDATE applications SET status = 'Interview Scheduled', "
        "interview_datetime = ?, interview_location = ? WHERE id = ?",
        (interview_datetime, interview_location, app_id),
    )
    db.commit()

    message = f"Interview scheduled for '{application['job_title']}' on {interview_datetime}"
    if interview_location:
        message += f" at {interview_location}"
    create_notification(db, application["user_id"], message, url_for("candidate_dashboard"))

    flash("Interview scheduled and candidate notified.", "success")
    return redirect(url_for("view_applicants", job_id=application["job_id"]))


# ----------------------------------------------------------------------------
# Notification routes
# ----------------------------------------------------------------------------
@app.route("/notifications")
@login_required
def notifications_page():
    db = get_db()
    notifs = db.execute(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()
    return render_template("notifications.html", notifications=notifs)


@app.route("/notifications/read/<int:notif_id>", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    db = get_db()
    db.execute(
        "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
        (notif_id, session["user_id"]),
    )
    db.commit()
    return redirect(request.referrer or url_for("home"))


@app.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (session["user_id"],))
    db.commit()
    flash("All notifications marked as read.", "info")
    return redirect(request.referrer or url_for("notifications_page"))


# ----------------------------------------------------------------------------
# Profile routes
# ----------------------------------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    user = current_user()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        skills = request.form.get("skills", "").strip()
        experience = request.form.get("experience", "").strip()
        company_name = request.form.get("company_name", "").strip()

        profile_pic = user["profile_pic"]
        pic_file = request.files.get("profile_pic")
        if pic_file and pic_file.filename:
            if allowed_file(pic_file.filename, ALLOWED_IMAGE_EXT):
                os.makedirs(PROFILE_FOLDER, exist_ok=True)
                filename = secure_filename(f"user{user['id']}_{pic_file.filename}")
                pic_file.save(os.path.join(PROFILE_FOLDER, filename))
                profile_pic = filename
            else:
                flash("Profile picture must be PNG, JPG, or GIF.", "danger")

        resume_file = user["resume_file"]
        resume = request.files.get("resume")
        if resume and resume.filename:
            if allowed_file(resume.filename, ALLOWED_RESUME_EXT):
                os.makedirs(RESUME_FOLDER, exist_ok=True)
                filename = secure_filename(f"user{user['id']}_{resume.filename}")
                resume.save(os.path.join(RESUME_FOLDER, filename))
                resume_file = filename
            else:
                flash("Resume must be a PDF, DOC, or DOCX file.", "danger")

        db.execute(
            "UPDATE users SET name=?, phone=?, skills=?, experience=?, company_name=?, "
            "profile_pic=?, resume_file=? WHERE id=?",
            (name, phone, skills, experience, company_name, profile_pic, resume_file, user["id"]),
        )
        db.commit()
        session["name"] = name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ----------------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    db_module.init_db()
    app.run(debug=True)
