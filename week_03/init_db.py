import os
from database import init_db, execute_db, query_db


def seed_courses():
    courses = [
        {
            "name": "Modern Web Development with React",
            "category": "Web Development",
            "duration": "12 Hours",
            "description": "Master React, hooks, state management, and modern CSS layouts to build premium single-page applications. From core concepts to production-grade deployment.",
            "image_url": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=600&q=80",
            "syllabus": "Introduction to React;JSX & Functional Components;State & Props;React Hooks (useState, useEffect);Context API & State Management;API Integration & Data Fetching;Routing with React Router;Deploying React Apps"
        },
        {
            "name": "Python Programming & Practical Applications",
            "category": "Programming",
            "duration": "8 Hours",
            "description": "Learn Python from scratch. Master fundamental syntax, object-oriented programming, file handling, web scraping, and automation scripting.",
            "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80",
            "syllabus": "Python Setup & Basics;Control Flow & Loops;Data Structures (Lists, Dicts);Functions & Scope;Object-Oriented Programming (OOP);File I/O & Error Handling;Working with APIs;Final Capstone Project"
        },
        {
            "name": "Introduction to Data Science & ML",
            "category": "Data Science",
            "duration": "16 Hours",
            "description": "Explore statistics, clean data using Pandas, create striking data visualizations, and build predictive machine learning models with Scikit-Learn.",
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80",
            "syllabus": "Data Science Overview;Pandas & NumPy Basics;Data Cleaning Techniques;Exploratory Data Analysis (EDA);Data Visualization (Matplotlib, Seaborn);Supervised Learning (Regression & Classification);Unsupervised Learning (K-Means);Model Evaluation"
        },
        {
            "name": "UX/UI Design Foundations",
            "category": "Design",
            "duration": "10 Hours",
            "description": "Understand user research, wireframing, high-fidelity UI design using Figma, grid layouts, typography, and interactive prototyping principles.",
            "image_url": "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?auto=format&fit=crop&w=600&q=80",
            "syllabus": "UX Design Thinking;User Research & Empathy Maps;Information Architecture;Wireframing Basics;Figma Interface & Layouts;Color Theory & Typography;Prototyping & Micro-interactions;Usability Testing"
        },
        {
            "name": "Deep Learning & Neural Networks",
            "category": "AI & ML",
            "duration": "20 Hours",
            "description": "Build deep neural networks. Explore Convolutional Networks (CNNs) for vision, Recurrent Networks (RNNs) for text, and modern transformer architectures.",
            "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=600&q=80",
            "syllabus": "Linear Algebra & Calculus recap;Neural Networks from Scratch;Introduction to PyTorch;Convolutional Neural Networks (CNNs);Recurrent Neural Networks (RNNs);Attention Mechanisms & Transformers;Generative AI Basics;Optimizing & Tuning Models"
        },
        {
            "name": "Creative Brand Identity Design",
            "category": "Design",
            "duration": "6 Hours",
            "description": "Learn the secrets of typography, color psychology, custom logo design, and crafting complete brand style guides for real-world clients.",
            "image_url": "https://images.unsplash.com/photo-1626785774573-4b799315345d?auto=format&fit=crop&w=600&q=80",
            "syllabus": "What is Brand Identity?;Visual Research & Moodboards;Typography Rules;Color Theory in Branding;Logo Concept Generation;Vector Illustration in Illustrator;Creating Brand Guidelines;Client Delivery Assets"
        }
    ]

    # Check if courses are already seeded
    existing_count = query_db("SELECT COUNT(*) as count FROM Courses", one=True)
    if existing_count and existing_count['count'] > 0:
        print("Courses already seeded.")
        return

    for course in courses:
        execute_db(
            "INSERT INTO Courses (name, category, duration, description, image_url, syllabus) VALUES (?, ?, ?, ?, ?, ?)",
            (course['name'], course['category'], course['duration'], course['description'], course['image_url'],
             course['syllabus'])
        )
    print("Database successfully seeded with courses!")


if __name__ == '__main__':
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    print("Initializing database...")
    init_db(schema_path)
    print("Seeding courses...")
    seed_courses()
    print("Initialization complete!")