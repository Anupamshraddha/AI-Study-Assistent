## StudyAI - AI MCQ Generator (Flask Project)

An AI-powered web application that generates MCQ questions automatically using LLM (Ollama / LLaMA3).

Built using Flask + Python + HTML/CSS + JavaScript.

##### Features
🤖 AI-powered MCQ generation
📚 Custom subject & topic selection
🎯 Difficulty level control (Easy / Medium / Hard)
🧠 Auto explanation for answers
🔐 User authentication (Login / Signup)
📊 Dashboard system
⚡ Fast and dynamic quiz generation
💾 JSON-based quiz handling
🛠️ Technologies Used

Python 3
Flask
Flask-Login
Flask-SQLAlchemy
HTML5
CSS3
JavaScript
Ollama (LLaMA3 model)

📦 Installation Guide
1️⃣ Clone the Repository
git clone (https://github.com/Anupamshraddha/AI-Study-Assistent)
cd studyai


Activate it:

3️⃣ Install Required Libraries
pip install flask
pip install flask-login
pip install flask-sqlalchemy
pip install ollama
4️⃣ Install Ollama (IMPORTANT)

Download Ollama:

👉 https://ollama.com/download

Then install model:

ollama run llama3
▶️ How to Run the Project
python app.py

Then open in browser:

http://127.0.0.1:5000/
🧪 How to Use

  Open the website
  
  Sign up / Login
  
  Go to Dashboard
  
  Open MCQ Generator
    Enter:
    Subject (e.g. Science)
    Topic (e.g. Electricity)
    Difficulty (Easy/Medium/Hard)
    Number of Questions
    Click Generate
    AI will create MCQ quiz instantly
    
📁 Project Structure
studyai/
│
├── app.py
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── index.html
│   ├── dashboard.html
│   ├── quiz.html
│   ├── mcq.html
│
├── static/
│   ├── css/
│       ├── style.css
│
└── README.md


⚠️ Important Notes
Make sure Ollama is running before starting Flask
Use stable internet for first model download
If JSON error happens, restart Ollama model
