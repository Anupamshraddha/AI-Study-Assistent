from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from PyPDF2 import PdfMerger, PdfReader
from PIL import Image
import io

from docx import Document
from fpdf import FPDF

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)


app.config["SECRET_KEY"] = "study-ai-secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)



login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(100)
    )


    email = db.Column(
        db.String(100),
        unique=True
    )


    password = db.Column(
        db.String(200)
    )



@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))



UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# HOME

@app.route("/")
def home():
    return render_template("index.html")


class Chat(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(
        db.String(100)
    )

    messages = db.Column(
        db.Text,
        default="[]"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )




# ---------------- CHAT PAGE ----------------


@app.route("/chat", methods=["GET","POST"])
@login_required
def chat():


    # create first chat

    if "chat_id" not in session:


        new = Chat(

            user_id=current_user.id,

            title="New Chat",

            messages="[]"

        )


        db.session.add(new)

        db.session.commit()


        session["chat_id"] = new.id



    chat = Chat.query.get(
        session["chat_id"]
    )


    messages = json.loads(
        chat.messages
    )



    if request.method=="POST":


        user_message = request.form["message"]



        messages.append({

            "role":"user",

            "content":user_message

        })



        try:


            response = ollama.chat(

                model="phi3",

                messages=[

                    {

                    "role":"system",

                    "content":
                    """
                    You are StudyAI.
                    Explain concepts simply.
                    Help with exams,
                    notes, MCQ and coding.
                    """

                    },

                    *messages

                ]

            )


            ai_message = response[
                "message"
            ][
                "content"
            ]



        except Exception as e:

            ai_message = (
                "AI error. Start Ollama."
            )



        messages.append({

            "role":"assistant",

            "content":ai_message

        })



        chat.messages=json.dumps(
            messages
        )


        if chat.title=="New Chat":

            chat.title=user_message[:25]


        db.session.commit()



    chats = Chat.query.filter_by(

        user_id=current_user.id

    ).order_by(
        Chat.id.desc()
    ).all()



    return render_template(
        "chat.html",
        messages=messages,
        chats=chats
    )






# ---------------- NEW CHAT ----------------


@app.route("/new_chat")
@login_required
def new_chat():


    chat = Chat(

        user_id=current_user.id,

        title="New Chat",

        messages="[]"

    )


    db.session.add(chat)

    db.session.commit()


    session["chat_id"]=chat.id


    return redirect("/chat")







# ---------------- LOAD CHAT ----------------


@app.route("/load_chat/<int:id>")
@login_required
def load_chat(id):


    chat = Chat.query.get_or_404(id)



    if chat.user_id != current_user.id:

        return "Unauthorized"



    session["chat_id"]=id



    return redirect("/chat")



@app.route("/delete_chat/<int:id>")
@login_required
def delete_chat(id):

    chat = Chat.query.get_or_404(id)

    if chat.user_id != current_user.id:
        return "Unauthorized"


    db.session.delete(chat)
    db.session.commit()


    # if deleting current chat
    if session.get("chat_id") == id:
        session.pop("chat_id", None)


    return redirect("/chat")

# SIGNUP

@app.route("/signup", methods=["GET","POST"])
def signup():


    if request.method=="POST":


        name=request.form["name"]

        email=request.form["email"]

        password=request.form["password"]

        confirm=request.form["confirm"]



        if password != confirm:

            return "Password does not match"



        existing=User.query.filter_by(
            email=email
        ).first()



        if existing:

            return "User already exists"



        user=User(

            name=name,

            email=email,

            password=generate_password_hash(password)

        )


        db.session.add(user)

        db.session.commit()



        return redirect("/login")



    return render_template("signup.html")





# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():


    if request.method=="POST":


        email=request.form["email"]

        password=request.form["password"]



        user=User.query.filter_by(
            email=email
        ).first()



        if user and check_password_hash(
            user.password,
            password
        ):


            login_user(user)


            return redirect("/dashboard")



        return redirect("/login")



    return render_template("login.html")







# DASHBOARD

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html")






# CHATBOT








# AI PDF NOTES GENERATOR
@login_required
@app.route("/notes", methods=["GET", "POST"])
def notes():

    if request.method == "POST":

        pdf = request.files["pdf"]

        filename = secure_filename(pdf.filename)

        path = os.path.join(UPLOAD_FOLDER, filename)

        pdf.save(path)

        # Extract PDF text
        reader = PdfReader(path)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        # 🔥 CLEAN TEXT (IMPORTANT FIX)
        def clean_text(t):
            return t.encode("ascii", "ignore").decode("ascii")

        text = clean_text(text)

        notes_text = f"""
AI GENERATED NOTES

{text[:3000]}

Summary:
- Important points extracted
- Revise the above concepts
- Generated by StudyAI
"""

        output = "AI_Notes.pdf"

        pdf_file = os.path.join(UPLOAD_FOLDER, output)

        doc = FPDF()

        doc.add_page()
        doc.set_font("Arial", size=12)

        doc.multi_cell(0, 10, notes_text)

        doc.output(pdf_file)

        return send_file(pdf_file, as_attachment=True)

    return render_template("notes.html")

from flask import Flask, render_template, request
from flask_login import login_required
import json
import re
import ollama



@app.route("/mcq", methods=["GET", "POST"])
@login_required
def mcq():

    if request.method == "POST":

        subject = request.form.get("subject", "")
        topic = request.form.get("topic", "")
        level = request.form.get("difficulty", "")
        count = request.form.get("count", "5")

        prompt = f"""
Create {count} MCQ questions.

Subject: {subject}
Topic: {topic}
Difficulty: {level}

Return ONLY valid JSON in this format:

[
 {{
  "question": "Question here",
  "options": [
   "option 1",
   "option 2",
   "option 3",
   "option 4"
  ],
  "answer": "correct option",
  "explanation": "short explanation"
 }}
]
"""

        try:
            response = ollama.chat(
                model="llama3",
                messages=[
                    {
                        "role": "system",
                        "content": "You must return ONLY valid JSON. No explanation, no markdown, no extra text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            text = response["message"]["content"]

            print("========== AI RESPONSE ==========")
            print(text)

            # 🔥 safer JSON extraction
            match = re.search(r"\[.*\]", text, re.DOTALL)

            if not match:
                raise Exception("AI did not return valid JSON")

            json_data = match.group()
            quiz = json.loads(json_data)

            return render_template("quiz.html", quiz=quiz)

        except Exception as e:
            return render_template("mcq.html", error=str(e))



    return render_template("mcq.html")




    return render_template("mcq.html")

# FLASHCARDS
@login_required
@app.route("/flashcards", methods=["GET","POST"])
def flashcards():

    error = None
    cards = None


    if request.method == "POST":


        subject = request.form.get("subject")
        topic = request.form.get("topic")
        count = request.form.get("count")



        prompt = f"""

You are an AI study assistant.

Create {count} revision flashcards.

Subject:
{subject}

Topic:
{topic}


Rules:

- Do NOT create questions.
- Do NOT use question marks.
- Make fact based learning cards.
- Each card needs a title.
- Each card needs 3-5 important facts.
- Keep facts short and easy to revise.


Return ONLY valid JSON.

Example:

[
 {{
  "title":"Python Basics",
  "facts":
  [
   "Python is a high level programming language.",
   "Python uses indentation for code blocks.",
   "Python supports object oriented programming."
  ]
 }}
]

"""


        try:


            response = ollama.chat(

                model="llama3",

                messages=[
                    {
                    "role":"user",
                    "content":prompt
                    }
                ]

            )


            text = response["message"]["content"]


            print("AI FLASHCARD RESPONSE")
            print(text)



            # extract JSON

            start = text.find("[")

            end = text.rfind("]")



            if start == -1 or end == -1:

                raise Exception(
                    "AI did not return JSON"
                )


            json_text = text[start:end+1]



            cards = json.loads(
                json_text
            )



            # open result page


            return render_template(
                "flashcards_result.html",
                cards=cards
            )




        except Exception as e:


            error = str(e)




    return render_template(
        "flashcards.html",
        error=error
    )






# PLANNER
@login_required
@app.route("/planner", methods=["GET","POST"])
def planner():

    plan=None
    error=None


    if request.method=="POST":


        subject=request.form["subject"]
        topics=request.form["topics"]
        exam=request.form["exam"]
        hours=request.form["hours"]



        prompt=f"""

You are an AI study planner.

Create a complete study plan.

Subject:
{subject}


Topics to cover:
{topics}


Exam date:
{exam}


Available study time per day:
{hours} hours


Instructions:

- Decide the number of days yourself according to the exam date.
- Cover all topics.
- Add revision days.
- Add practice/test days.
- Make a realistic timetable.
- Do not limit to 3 days.
- Do not explain anything.

Return ONLY JSON.

Format:

[
 {{
  "day":"Day 1",
  "topic":"",
  "tasks":
  [
   "",
   "",
   ""
  ]
 }}
]

"""


        try:


            response=ollama.chat(

                model="llama3",

                messages=[
                    {
                    "role":"user",
                    "content":prompt
                    }
                ]

            )


            text=response["message"]["content"]


            start=text.find("[")

            end=text.rfind("]")


            plan=json.loads(
                text[start:end+1]
            )



            return render_template(
                "planner_result.html",
                plan=plan
            )



        except Exception as e:

            error=str(e)



    return render_template(
        "planner.html",
        error=error
    )




@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")

@app.route("/about")
def about():
    return render_template("about.html")
# PROFILE

@app.route("/profile")
@login_required
def profile():


    return render_template(
        "profile.html",
        user=current_user
    )








# PDF MERGER
@login_required
@app.route("/upload", methods=["POST"])
def upload_files():


    files=request.files.getlist("files")


    merger=PdfMerger()



    for file in files:


        filename=secure_filename(
            file.filename
        )


        path=os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        file.save(path)



        if filename.endswith(".pdf"):

            merger.append(path)



    result="final_output.pdf"


    merger.write(
        os.path.join(
            UPLOAD_FOLDER,
            result
        )
    )


    merger.close()



    return send_file(
        os.path.join(
            UPLOAD_FOLDER,
            result
        ),
        as_attachment=True
    )





@login_required
@app.errorhandler(404)
def error(e):

    return render_template(
        "404.html"
    )



if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)
