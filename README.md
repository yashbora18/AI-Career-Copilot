# AI Career Copilot (AI Based Resume Analyzer Groq) 🚀

AI Career Copilot is an AI-powered Resume Analyzer web application built using Flask, Groq AI, and SQLAlchemy. The application helps users analyze resumes, identify missing skills, generate interview questions, recommend job roles, and create personalized learning roadmaps using AI.

## ✨ Features

- 🔐 User Authentication (Signup/Login)
- 📄 Resume Upload (PDF & DOCX)
- 🤖 AI Resume Analysis using Groq API
- 📊 Resume Score Generation
- 🧠 Skill Extraction & Missing Skill Detection
- 🛣️ Personalized Career Roadmap
- 💼 Recommended Job Roles
- 🎯 Interview Question Suggestions
- 📥 Download Resume Report as PDF
- 🕘 Analysis History Tracking

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Backend
- Python
- Flask

### Database
- SQLAlchemy
- MySQL / TiDB

### AI Integration
- Groq API
- Llama 3 Model

### Libraries Used
- PyPDF2
- python-docx
- reportlab
- gunicorn

## 📂 Project Structure

AI-Career-Copilot/
│
├── static/
├── templates/
├── app.py
├── db.py
├── models.py
├── requirements.txt
├── README.md
└── .gitignore

⚙️ Installation
Clone Repository
git clone https://github.com/yashbora18/AI-Career-Copilot.git

Open Project
cd AI-Career-Copilot

Create Virtual Environment
python -m venv venv

Activate Environment (Windows)
venv\Scripts\activate

Install Dependencies
pip install -r requirements.txt

🔑 Environment Variables

Create .env file:

GROQ_API_KEY=your_api_key

▶️ Run Application
python app.py

Open browser:

http://127.0.0.1:5000

🚀 Deployment

This project can be deployed on:

Render

📸 Sample Output
{
  "score": 85,
  "skills": ["Python", "Flask", "SQL"],
  "missing_skills": ["Docker", "AWS"],
  "roadmap": ["Learn APIs", "Build Projects"],
  "interview_questions": ["Explain REST API"],
  "job_roles": ["Backend Developer"]
}
