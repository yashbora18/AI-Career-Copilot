from flask import Flask, render_template, request, redirect, session, send_file
from db import Base, engine, SessionLocal
import PyPDF2
import docx
import json
import models
from groq import Groq
from io import BytesIO

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "secret123"

client = Groq()

Base.metadata.create_all(bind=engine)

# AI FUNCTION
def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a senior hiring manager.

Analyze the resume based on goal: "{user_goal}"

Return ONLY JSON:
{{
"score": 0-100,
"skills": [],
"missing_skills": [],
"roadmap": [],
"interview_questions": [],
"job_roles": []
}}

Resume:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Strict hiring manager."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        return json.loads(content[start:end])

    except Exception as e:
        return {
            "score": 50,
            "skills": ["Python"],
            "missing_skills": ["Docker"],
            "roadmap": ["Build projects"],
            "interview_questions": ["Explain REST API"],
            "job_roles": ["Backend Developer"],
            "error": str(e)
        }

# HOME 
@app.route("/")
def home():
    if "users" in session:
        return redirect("/dashboard")
    return redirect("/login")

# SIGNUP 
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            return "User already exists"

        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()

        return redirect("/login")

    return render_template("signup.html")

# LOGIN 
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.query(models.User).filter_by(email=email, password=password).first()

        if user:
            session["users"] = user.email
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "users" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")
        file = request.files.get("file")

        # File handling
        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}

            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Docx error: {str(e)}"}

        if not resume_text:
            result = {"error": "Please upload or paste resume"}

        elif resume_text and user_goal:
            try:
                resume_text = resume_text[:4000]

                result = analyze_resume(resume_text, user_goal)

                #  SAVE RESULT FOR DOWNLOAD
                session["last_result"] = result

                db = SessionLocal()
                user = db.query(models.User).filter_by(email=session["users"]).first()

                report = models.Report(
                    user_id=user.id,
                    resume_text=resume_text,
                    results=json.dumps(result)
                )

                db.add(report)
                db.commit()

            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}

    return render_template(
        "dashboard.html",
        user=session["users"],
        result=result
    )

# HISTORY
@app.route("/history")
def history():
    if "users" not in session:
        return redirect("/login")

    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["users"]).first()

    reports = db.query(models.Report).filter_by(user_id=user.id).all()

    parsed_reports = []
    for r in reports:
        try:
            parsed_result = json.loads(r.results)
        except:
            parsed_result = {}

        parsed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })

    return render_template("history.html", reports=parsed_reports)

# DOWNLOAD PDF
@app.route("/download_pdf")
def download_pdf():
    if "users" not in session:
        return redirect("/login")

    result = session.get("last_result")

    if not result:
        return "No data to download"

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Resume Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Score: {result.get('score', 0)}/100", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Skills
    elements.append(Paragraph("Skills:", styles["Heading2"]))
    for s in result.get("skills", []):
        elements.append(Paragraph(f"- {s}", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # Missing Skills
    elements.append(Paragraph("Missing Skills:", styles["Heading2"]))
    for s in result.get("missing_skills", []):
        elements.append(Paragraph(f"- {s}", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # Roadmap
    elements.append(Paragraph("Roadmap:", styles["Heading2"]))
    for s in result.get("roadmap", []):
        elements.append(Paragraph(f"- {s}", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # Interview Questions
    elements.append(Paragraph("Interview Questions:", styles["Heading2"]))
    for s in result.get("interview_questions", []):
        elements.append(Paragraph(f"- {s}", styles["Normal"]))

    elements.append(Spacer(1, 12))

    # Job Roles
    elements.append(Paragraph("Recommended Roles:", styles["Heading2"]))
    for j in result.get("job_roles", []):
        elements.append(Paragraph(f"- {j}", styles["Normal"]))

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume_report.pdf",
        mimetype="application/pdf"
    )

# LOGOUT 
@app.route("/logout")
def logout():
    session.pop("users", None)
    return redirect("/login")

# RUN 
if __name__ == "__main__":
    app.run(debug=True)