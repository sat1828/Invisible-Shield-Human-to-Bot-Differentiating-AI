
```markdown
# 🤖 Human-Bot Differentiation AI

A hybrid, privacy-focused system that differentiates human users from bots using behavioral biometrics and CAPTCHA. Built entirely in **Python (Flask)** and **JavaScript**, this project operates fully **offline** and applies **heuristic analysis** on real-time mouse movements and keystroke dynamics to detect automation — without relying on cloud-based machine learning APIs.

---

## 🚀 Project Overview

Traditional CAPTCHA systems are no longer sufficient to detect modern bots that leverage OCR and AI to mimic human input. This project, titled **InvisibleShield**, introduces a dual-verification approach:

- CAPTCHA Verification: Image-based + audio CAPTCHA using PIL and pyttsx3.
- Behavioral Verification: Mouse movement and typing pattern analysis using JavaScript tracking and Flask-based heuristics.

The system determines authenticity by evaluating variability in input behavior — a trait difficult for bots to replicate.

---

## 🧩 Features

- 🔐 CAPTCHA verification (image and audio)
- 🖱️ Mouse movement tracking with jerk/velocity analysis
- ⌨️ Keystroke timing variability detection
- 🔁 Heuristic-based scoring (no ML dependency)
- 🌐 Full offline support (no external APIs)
- 📦 Flask REST API integration
- 💡 Modular design for easy integration into any web app
- 🧠 Feedback loop and session-based decision flow

---

## 📁 Project Structure

```

/static
├── css/              # Custom styles (auth, splash, main)
├── js/               # Behavior tracking and slider logic
/templates
├── index.html        # Splash screen
├── login.html        # Login with dual verification
├── signup.html       # Signup with verification
├── main.html         # Main landing page post-auth
/app.py                 # Flask backend routes and logic
/verification.js        # Client-side behavior tracking
captcha\_verification.py # GUI version of CAPTCHA (Tkinter)

````

---

## 🛠️ Tech Stack

- Python (Flask, PIL, pyttsx3)
- JavaScript (Vanilla JS for real-time tracking)
- HTML/CSS (Frontend interface)
- Tkinter (For standalone CAPTCHA demo)
- Flask-Session (Session and security)

---

## 📊 System Flow

1. User selects verification method: CAPTCHA or Behavior.
2. Behavior mode:
   - Mouse & typing data captured using JavaScript.
   - Sent to backend API for scoring.
3. CAPTCHA mode:
   - CAPTCHA image/audio generated locally.
   - Verified directly without any third-party service.
4. Verified users are authenticated; bots are denied.

---

## 📈 Performance Highlights

| Metric                      | CAPTCHA Only | Behavior Only | Combined |
|----------------------------|--------------|----------------|----------|
| False Positives (Bots passed) | 10%         | 6.67%          | 0%       |
| False Negatives (Humans blocked) | 0%     | 0%             | 0%       |
| Avg Response Time          | 540 ms       | 1120 ms        | 1300 ms  |

---

## 🧪 How to Run

```bash
# Clone repository
git clone https://github.com/your-username/human-bot-differentiation-ai.git
cd human-bot-differentiation-ai

# Set up virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
````

Visit `http://localhost:5000` in your browser to test.

---

## 🧠 Future Scope

* Adaptive heuristics based on user profiles
* Touchscreen/tap behavior integration
* Behavior-based CAPTCHA fallback models

---

## 🔗 Contact

**Developer:** \[Satyajit Parida]
**Email:** [satyajitparida294@gmail.com](mailto:satyajitparida294@gmail.com)
**LinkedIn:** [https://www.linkedin.com/in/satyajit-parida-48a34230a/ ](https://www.linkedin.com/in/satyajit-parida-48a34230a/ ))
