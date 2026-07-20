CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    bio TEXT,
    join_date TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS Courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    duration TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT,
    syllabus TEXT
);

CREATE TABLE IF NOT EXISTS Enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    enrollment_date TEXT DEFAULT (datetime('now', 'localtime')),
    completion_date TEXT,
    certificate_id TEXT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses (id) ON DELETE CASCADE,
    UNIQUE (user_id, course_id)
);