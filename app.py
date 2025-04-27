from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import secrets
import random
import string
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
import json
import time
from datetime import datetime
import pyttsx3
from flask_session import Session

app = Flask(__name__)
app.secret_key = "a27f3ee02cb4e5992e2858cc4c4235a06202e36f5496a8d9c528a32dc0e3e274"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Simulate database with in-memory storage (replace with actual DB in production)
users_db = {}
bot_logs = []

# CAPTCHA Functions
def generate_captcha_text(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_captcha_image(text):
    width, height = 250, 100
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except IOError:
        font = ImageFont.load_default()
    for _ in range(500):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)), width=2)
    for i, char in enumerate(text):
        x = random.randint(20 + i * 30, 40 + i * 35)
        y = random.randint(5, 40)
        draw.text((x, y), char, font=font, fill=(0, 0, 0))
    image = image.filter(ImageFilter.GaussianBlur(1.5))
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def create_audio_captcha(text):
    audio_path = "static/captcha_audio.wav"
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    return audio_path

# Behavioral Verification Class
class BehaviorVerification:
    def __init__(self):
        self.velocity_threshold = 2.5
        self.typing_speed_threshold = 8.0
        self.typing_variability_threshold = 0.3

    def analyze_mouse_movement(self, positions, timestamps):
        timestamps = [t/1000 for t in timestamps]
        if len(positions) < 3:
            return {"is_human": False, "reason": "Not enough movement data"}
        velocities = []
        for i in range(1, len(positions)):
            dt = timestamps[i] - timestamps[i-1]
            if dt == 0:
                continue
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            velocity = np.sqrt(dx**2 + dy**2) / dt
            velocities.append(velocity)
        if not velocities:
            return {"is_human": False, "reason": "Could not calculate velocities"}
        velocity_std = np.std(velocities)
        is_human = velocity_std >= self.velocity_threshold
        return {"is_human": is_human, "score": velocity_std, "threshold": self.velocity_threshold}

    def analyze_typing_pattern(self, keystroke_times, text_length, total_time):
        if len(keystroke_times) < 3:
            return {"is_human": False, "reason": "Not enough keystroke data"}
        typing_speed = text_length / total_time
        keystroke_intervals = [keystroke_times[i] - keystroke_times[i-1] 
                                for i in range(1, len(keystroke_times))]
        mean_interval = np.mean(keystroke_intervals)
        std_interval = np.std(keystroke_intervals)
        variability = std_interval / mean_interval if mean_interval > 0 else 0
        is_human = (typing_speed <= self.typing_speed_threshold and 
                    variability >= self.typing_variability_threshold)
        return {"is_human": is_human, "typing_speed": typing_speed, "variability": variability}

    def analyze_mouse_advanced(self, positions, timestamps, velocity_fluctuation, jerk_fluctuation):
        if velocity_fluctuation > 1.5 and jerk_fluctuation > 2.0:
            return {"is_human": True}
        else:
            return {"is_human": False, "reason": "Unnatural Mouse Movements"}

    def analyze_typing_advanced(self, keystroke_times, text_length, total_time, keypress_variability):
        avg_speed = text_length / total_time if total_time > 0 else 0
        if avg_speed < 9 and keypress_variability > 0.05:
            return {"is_human": True}
        else:
            return {"is_human": False, "reason": "Unnatural Typing"}

verifier = BehaviorVerification()

sentence_list = [
    "AI is transforming daily life",
    "Python is an amazing language",
    "I enjoy coding and problem solving",
    "Machine learning is a fascinating field",
    "Data science is the future of technology",
    "The sky is clear and blue",
    "Autonomous vehicles are shaping the future",
    "Blockchain technology ensures secure transactions",
    "The stars twinkle at night",
    "Coding challenges improve logical thinking",
    "Nature offers endless inspiration",
    "Robots can now perform complex tasks",
    "Reading expands the horizons of the mind",
    "Artificial intelligence simulates human intelligence",
    "Deep learning models require large datasets",
    "Success comes through persistent effort",
    "Innovation drives technological progress",
    "Cloud computing offers scalable solutions",
    "Clean energy is vital for sustainability",
    "The universe is vast and mysterious",
    "Quantum computing is the future frontier",
    "Exploring different cuisines broadens cultural understanding",
    "Cybersecurity protects against digital threats",
    "Teamwork fosters collective success",
    "Augmented reality enhances real-world experiences",
    "Mathematics is the language of science",
    "Birds chirp melodiously in the morning",
    "Recycling helps conserve the environment",
    "Learning from failures leads to growth",
    "Space exploration expands our knowledge of the cosmos",
    "Smart homes improve daily convenience",
    "Electric vehicles contribute to a cleaner planet",
    "Empathy strengthens human connections",
    "Time management boosts productivity",
    "Healthy eating supports mental and physical well-being",
    "Every sunrise offers a new opportunity",
    "History teaches valuable lessons",
    "Music has the power to uplift spirits",
    "Artificial neural networks mimic human brains",
    "Creativity is the essence of artistic expression",
    "Philosophy encourages deep thinking and reflection",
    "Sustainability ensures a brighter future",
    "Embracing challenges builds resilience",
    "Science fiction inspires technological innovation",
    "The internet connects people across the world",
    "Problem-solving skills are essential in every field",
    "Volunteering promotes community growth",
    "Biotechnology advances healthcare solutions",
    "Renewable energy reduces carbon emissions",
    "Knowledge sharing fosters collective progress"
]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/signup')
def signup():
    session['captcha_text'] = generate_captcha_text()
    captcha_image = create_captcha_image(session['captcha_text'])
    return render_template('signup.html', captcha_image=captcha_image)

@app.route('/login')
def login():
    session['captcha_text'] = generate_captcha_text()
    captcha_image = create_captcha_image(session['captcha_text'])
    return render_template('login.html', captcha_image=captcha_image)

@app.route('/api/generate-captcha')
def generate_captcha():
    session['captcha_text'] = generate_captcha_text()
    img_str = create_captcha_image(session['captcha_text'])
    return f"data:image/png;base64,{img_str}"

@app.route('/verify', methods=['POST'])
def verify():
    user_input = request.form['captcha_input']
    if user_input.strip().upper() == session.get('captcha_text'):
        session['verified'] = True
        return jsonify({"success": True, "message": "CAPTCHA Verified!"})
    else:
        session['verified'] = False
        return jsonify({"success": False, "message": "Incorrect CAPTCHA"})

@app.route('/refresh', methods=['POST'])
def refresh():
    session['captcha_text'] = generate_captcha_text()
    captcha_image = create_captcha_image(session['captcha_text'])
    return jsonify({"captcha_image": captcha_image})

@app.route('/audio')
def get_audio():
    audio_path = create_audio_captcha(session.get('captcha_text'))
    return send_file(audio_path, mimetype='audio/wav')

@app.route('/verify-mouse-movement', methods=['POST'])
def verify_mouse():
    data = request.json
    positions = data.get('positions', [])
    timestamps = data.get('timestamps', [])
    result = verifier.analyze_mouse_movement(positions, timestamps)
    if result['is_human']:
        session['verified'] = True
    return jsonify(result)

@app.route('/verify-typing', methods=['POST'])
def verify_typing():
    data = request.json
    keystroke_times = data.get('keystrokeTimes', [])
    text_length = data.get('textLength', 0)
    total_time = data.get('totalTime', 0)
    result = verifier.analyze_typing_pattern(keystroke_times, text_length, total_time)
    if result['is_human']:
        session['verified'] = True
    return jsonify(result)

@app.route('/api/verify-captcha', methods=['POST'])
def verify_captcha():
    data = request.json
    user_input = data.get('captcha', '').strip().upper()
    correct_captcha = session.get('captcha_text', '')
    if user_input == correct_captcha:
        session['verified'] = True
        return jsonify({"success": True})
    else:
        session['verified'] = False
        return jsonify({"success": False, "message": "Incorrect CAPTCHA."})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    if not session.get('verified', False):
        return jsonify({"success": False, "message": "Please complete verification first"})
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    if not all([fullname, email, phone, password]):
        return jsonify({"success": False, "message": "All fields are required."})
    if email in users_db:
        return jsonify({"success": False, "message": "User already exists with this email."})
    users_db[email] = {
        "fullname": fullname,
        "email": email,
        "phone": phone,
        "password": password,
        "created_at": datetime.now().isoformat()
    }
    session.pop('verified', None)
    return jsonify({"success": True, "message": "Account created successfully!", "redirect": "/main"})

@app.route('/api/login', methods=['POST'])
def api_login():
    if not session.get('verified', False):
        return jsonify({"success": False, "message": "Please complete verification first"})
    email = request.form.get('email')
    password = request.form.get('password')
    if not all([email, password]):
        return jsonify({"success": False, "message": "Email and password are required."})
    user = users_db.get(email)
    if not user or user['password'] != password:
        return jsonify({"success": False, "message": "Invalid email or password."})
    session.pop('verified', None)
    return jsonify({"success": True, "message": "Login successful!", "redirect": "/main"})

@app.route('/api/log-bot-detection', methods=['POST'])
def log_bot_detection():
    data = request.json
    bot_logs.append({
        "page": data.get('page'),
        "timestamp": data.get('timestamp'),
        "ip": request.remote_addr
    })
    return jsonify({"success": True})

@app.route('/verify-mouse-advanced', methods=['POST'])
def verify_mouse_advanced():
    data = request.json
    positions = data.get('positions', [])
    timestamps = data.get('timestamps', [])
    velocity_fluctuation = data.get('velocityFluctuation', 0)
    jerk_fluctuation = data.get('jerkFluctuation', 0)
    result = verifier.analyze_mouse_advanced(positions, timestamps, velocity_fluctuation, jerk_fluctuation)
    if result['is_human']:
        session['verified'] = True
    return jsonify(result)

@app.route('/verify-typing-advanced', methods=['POST'])
def verify_typing_advanced():
    data = request.json
    keystroke_times = data.get('keystrokeTimes', [])
    text_length = data.get('textLength', 0)
    total_time = data.get('totalTime', 0)
    keypress_variability = data.get('keypressVariability', 0)
    result = verifier.analyze_typing_advanced(keystroke_times, text_length, total_time, keypress_variability)
    if result['is_human']:
        session['verified'] = True
    return jsonify(result)

@app.route('/api/generate-sentence')
def generate_sentence():
    sentence = random.choice(sentence_list)
    return jsonify({"sentence": sentence})

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)