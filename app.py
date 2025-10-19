from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import pymysql
import pymysql.cursors
from datetime import datetime, timedelta, time as dt_time, date
import random
from twilio.rest import Client
import re
import uuid
import cv2
import time

# AI Chatbot Imports
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
import google.generativeai as genai

# Facial Recognition Imports
from facial_recognition import detect_emotion, save_emotion_log, get_emotion_history, load_models

# ---------------- Load Environment Variables ----------------
load_dotenv()

# --- AI Chatbot Configuration ---
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Explicitly configure the Google AI client with the API key
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in .env file.")

# ---------------- Database Connection Details ----------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    # FIX: The default password for a standard XAMPP/MariaDB installation is an empty string.
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "udaan_db"),
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True
}

def get_db_connection():
    """Establishes a new database connection."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        return None

# ---------------- Flask App ----------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

# --- Load Facial Recognition Models on Startup ---
with app.app_context():
    try:
        print("Loading facial recognition models...")
        load_models()
        print("Facial recognition models loaded successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load facial recognition models: {e}")
        print("The facial analysis feature will not work.")


# --- Crisis Detection and Emergency Call ---
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life", 
    "ending it all", "self-harm", "suicidal"
]

def detect_crisis(text):
    """
    Checks if the user's text contains any crisis keywords.
    """
    for keyword in CRISIS_KEYWORDS:
        if keyword in text.lower():
            return True
    return False

def make_emergency_call():
    """
    Uses Twilio to make an emergency call to the number in the .env file.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    emergency_number = os.getenv("EMERGENCY_PHONE_NUMBER")

    if not all([account_sid, auth_token, twilio_number, emergency_number]):
        print("\n[ALERT] Twilio credentials or emergency number not found in .env file. Cannot make call.")
        return

    try:
        client = Client(account_sid, auth_token)
        print("\n[CRISIS DETECTED] Initiating emergency call...")
        
        call = client.calls.create(
            twiml='<Response><Say>Hello. This is an automated alert from the Udaan AI Companion. A user has expressed thoughts of self-harm. Please follow up immediately.</Say></Response>',
            to=emergency_number,
            from_=twilio_number
        )
        print(f"[SUCCESS] Call initiated with SID: {call.sid}")

    except Exception as e:
        print(f"\n[ERROR] Failed to initiate Twilio call: {e}")


# ---------------- AI Chatbot Setup ----------------
chain = None
docsearch = None
try:
    print("Initializing AI Chatbot...")
    prompt_template = """
    You are "Udaan AI Companion," a caring and supportive AI designed to help students with their mental wellness. Your tone should always be empathetic, patient, and non-judgmental. Your goal is to guide users to the platform's features when appropriate.

    **Safety First:**
    - If the user mentions any intention of self-harm, suicide, or harming others, you MUST immediately respond with a message encouraging them to seek professional help and provide a generic helpline number. Example: "It sounds like you are going through a difficult time. Please consider reaching out to a crisis hotline or a mental health professional. You can call a local crisis line or the National Suicide Prevention Lifeline at 988. Your well-being is very important."

    **Answering Guidelines & Feature Integration:**
    
    **Rule 1: Handle Simple Greetings (Top Priority)**
    - If the user's message is ONLY a simple greeting (e.g., "hi", "hello", "hey", "how are you"), you MUST respond with a short, friendly, and direct conversational reply. 
    - **DO NOT** suggest features or ask a lot of follow-up questions for simple greetings.
    - Example for "hi": "Hello! How can I help you today?"
    - Example for "how are you": "I'm an AI, so I don't have feelings, but I'm here and ready to help you. What's on your mind?"

    **Rule 2: Detect User Needs & Suggest Features**
    - If the user's message is more than just a simple greeting and expresses feelings, problems, or asks a question, then you should identify their need and suggest a relevant platform feature. Use the exact markdown format with the `url_for` placeholder.
        - If the user feels sad, depressed, or hopeless, suggest: "It sounds like you're having a tough time. It might be helpful to understand these feelings better. You can take our confidential PHQ-9 assessment for depression. [Take the PHQ-9 Assessment]({{url_for('student_assessment', assessment_name='phq9')}})"
        - If the user feels anxious, worried, or stressed, suggest: "Feeling anxious can be overwhelming. To get a clearer picture of what you're experiencing, you could take the GAD-7 assessment. [Take the GAD-7 Assessment]({{url_for('student_assessment', assessment_name='gad7')}})"
        - If the user wants to write down their thoughts, suggest: "Writing down your feelings can be a great way to process them. You might find our Wellness Journal helpful. [Open Your Wellness Journal]({{url_for('student_journal')}})"
        - If the user wants to talk to a professional, suggest: "Taking the step to talk to a professional is a sign of strength. You can book a confidential appointment with a counselor. [Book an Appointment]({{url_for('student_booking')}})"
        - If the user wants to talk to a peer or ask a question anonymously, suggest: "Connecting with peers can make a big difference. Our Peer Forum is a safe, anonymous space to share and ask questions. [Go to the Peer Forum]({{url_for('student_forum')}})"
        - If the user is looking for information (e.g., "how to manage stress"), suggest: "I can help with that. We have a collection of articles and videos in our Resources section that you might find helpful. [Explore Resources]({{url_for('student_resources')}})"
        - If the user feels bored, tired, burned out, needs a break, or wants to relax, suggest: "Taking a break is important for your well-being. We have some games, guided meditations, and relaxing music in our Curricular Activities section. [Find an Activity]({{url_for('student_activities')}})"
        - If the user wants to analyze their facial expression or understand their emotions visually, suggest: "It can be insightful to see how you're expressing your emotions. Our Facial Analysis feature can help with that. [Try Facial Analysis]({{url_for('student_facial_expression')}})"
    
    **Rule 3: Use General Context**
    - For questions not directly matching a feature, use the provided context to answer. If the context is irrelevant, state you can't find specific information but are there to offer general support.

    Context: {context}
    Question: {question}

    Based on the rules above, provide a helpful and supportive answer.
    Helpful answer:
    """
    
    embeddings = download_embeddings()
    index_name = "udaan-chatbot" 
    docsearch = PineconeVectorStore.from_existing_index(index_name, embeddings)
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    # FIX: Switched from 'gemini-pro' to 'gemini-1.5-flash-latest' to match available free-tier models.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.8)
    chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)
    print("AI Chatbot initialized successfully.")
except Exception as e:
    print(f"Failed to initialize AI Chatbot: {e}")


# ---------------- Anonymous Names for Forum ----------------
ANONYMOUS_ADJECTIVES = ["Brave", "Calm", "Curious", "Daring", "Eager", "Fearless", "Gentle", "Happy", "Jolly", "Kind", "Lively", "Merry", "Nice", "Proud", "Silly", "Wise", "Zany"]
ANONYMOUS_NOUNS = ["Panda", "Lion", "Tiger", "Bear", "Eagle", "Dolphin", "Fox", "Wolf", "Hawk", "Owl", "Cat", "Dog", "Koala", "Penguin", "Rabbit", "Squirrel", "Turtle"]

def get_anonymous_name(user_id):
    """Generates a consistent anonymous name based on user ID."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return "Anonymous User"
    adj_index = (user_id * 7) % len(ANONYMOUS_ADJECTIVES)
    noun_index = (user_id * 13) % len(ANONYMOUS_NOUNS)
    return f"{ANONYMOUS_ADJECTIVES[adj_index]} {ANONYMOUS_NOUNS[noun_index]}"


# ---------------- Helper Functions & Hooks ----------------

def get_global_context():
    """Fetches all platform settings and context data from the DB."""
    context = {"settings": {}, "emergency_contact": None, "get_anonymous_name": get_anonymous_name}
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT setting_key, setting_value FROM platform_settings")
                settings_data = cursor.fetchall()
                settings = {item['setting_key']: item['setting_value'] for item in settings_data}
                contact_name = settings.get('emergency_contact_name')
                contact_number = settings.get('emergency_contact_number')
                if contact_name and contact_number:
                    context["emergency_contact"] = {'name': contact_name, 'number': contact_number}
                context["settings"] = settings
        finally:
            conn.close()
    return context

def get_assessment_interpretation(assessment_type, score):
    """Provides interpretation and suggestions based on assessment score."""
    interpretation = {'show_urgent_suggestions': False, 'linked_suggestions': []}
    if assessment_type == 'PHQ-9':
        if score <= 4:
            interpretation.update({
                'level': 'Minimal depression',
                'description': "Your score suggests you are experiencing minimal or no symptoms of depression. Keep up with your healthy habits!",
                'suggestions': [
                    "Continue engaging in regular physical activity.",
                    "Practice mindfulness or meditation to maintain your well-being.",
                    "Connect with friends and pursue your hobbies."
                ]
            })
        elif score <= 9:
            interpretation.update({
                'level': 'Mild depression',
                'description': "Your score suggests you may be experiencing mild symptoms of depression. It's a good time to focus on self-care.",
                'suggestions': [
                    "Explore our guided meditations and relaxation music in the Activities section.",
                    "Try journaling your thoughts and feelings daily.",
                    "Consider talking to a trusted friend, family member, or peer supporter in our forum."
                ]
            })
        elif score <= 14:
            interpretation.update({
                'level': 'Moderate depression',
                'description': "Your score suggests you are experiencing moderate symptoms of depression. It's important to take these feelings seriously and seek support.",
                'suggestions': [
                    "We strongly recommend booking an appointment with one of our counselors.",
                    "Check out the articles and videos on managing depression in our Resources section.",
                    "Establishing a routine can be very helpful. Try to maintain regular sleep, meal, and exercise schedules."
                ],
                'show_urgent_suggestions': True,
                'linked_suggestions': [
                    {'text': 'Book a confidential appointment with a counselor.', 'url_key': 'student_booking'},
                    {'text': 'Explore relaxation exercises and mindful games.', 'url_key': 'student_activities'}
                ]
            })
        elif score <= 19:
            interpretation.update({
                'level': 'Moderately severe depression',
                'description': "Your score indicates moderately severe symptoms of depression. Professional help is highly recommended at this stage.",
                'suggestions': [
                    "Please book an appointment with a counselor as soon as possible.",
                    "It is crucial to talk to someone. If you feel overwhelmed, please reach out to the emergency contact provided on your dashboard.",
                    "Avoid isolation. Reach out to supportive people in your life, even if you don't feel like it."
                ],
                'show_urgent_suggestions': True,
                'linked_suggestions': [
                    {'text': 'Book a confidential appointment with a counselor.', 'url_key': 'student_booking'},
                    {'text': 'View our curated wellness resources.', 'url_key': 'student_resources'}
                ]
            })
        else:
            interpretation.update({
                'level': 'Severe depression',
                'description': "Your score suggests severe symptoms of depression. Please prioritize seeking professional help immediately.",
                'suggestions': [
                    "Your well-being is the top priority. Please book an appointment with a counselor now.",
                    "If you are having thoughts of harming yourself, please contact the emergency support line immediately.",
                    "Allow others to help you. You do not have to go through this alone."
                ],
                'show_urgent_suggestions': True,
                'linked_suggestions': [
                    {'text': 'Book a confidential appointment now.', 'url_key': 'student_booking'},
                    {'text': 'See the emergency contact on your dashboard.', 'url_key': 'student_dashboard'}
                ]
            })
    elif assessment_type == 'GAD-7':
        if score <= 4:
            interpretation.update({
                'level': 'Minimal anxiety',
                'description': "Your score suggests minimal or no anxiety. This is a great sign of your current mental well-being.",
                'suggestions': [
                    "Engage in relaxing activities to maintain this state.",
                    "Practice deep breathing exercises regularly.",
                    "Explore the Curricular Activities section for stress-relieving games and music."
                ]
            })
        elif score <= 9:
            interpretation.update({
                'level': 'Mild anxiety',
                'description': "Your score indicates you may be experiencing mild symptoms of anxiety. Focusing on coping strategies can be very beneficial.",
                'suggestions': [
                    "Try the mindfulness exercises in our Resources section.",
                    "Journaling can help you understand and manage your worries.",
                    "Limit caffeine and ensure you are getting enough sleep."
                ]
            })
        elif score <= 14:
            interpretation.update({
                'level': 'Moderate anxiety',
                'description': "Your score suggests moderate symptoms of anxiety. It's a good idea to seek support to learn effective management techniques.",
                'suggestions': [
                    "We recommend booking an appointment with a counselor to discuss how you're feeling.",
                    "Explore resources on anxiety management.",
                    "Challenge anxious thoughts by questioning their validity and focusing on the present moment."
                ],
                'show_urgent_suggestions': True,
                'linked_suggestions': [
                    {'text': 'Book an appointment to talk with a professional.', 'url_key': 'student_booking'},
                    {'text': 'Try a guided meditation from our Activities.', 'url_key': 'student_activities'}
                ]
            })
        else:
            interpretation.update({
                'level': 'Severe anxiety',
                'description': "Your score indicates severe symptoms of anxiety. It is very important to seek professional support.",
                'suggestions': [
                    "Please prioritize booking an appointment with a counselor.",
                    "If you are feeling overwhelmed or having a panic attack, focus on your breathing. Inhale for 4 seconds, hold for 4, and exhale for 6.",
                    "Reach out to the emergency contact on your dashboard if you are in immediate distress."
                ],
                'show_urgent_suggestions': True,
                'linked_suggestions': [
                    {'text': 'Book an appointment now.', 'url_key': 'student_booking'},
                    {'text': 'Find helpful articles in our Resources section.', 'url_key': 'student_resources'}
                ]
            })
    elif assessment_type == 'GHQ-12':
        if score <= 3:
            interpretation.update({
                'level': 'Low psychological distress',
                'description': "Your score suggests a low level of psychological distress, indicating good general mental health.",
                'suggestions': [
                    "Keep investing in your well-being through positive social connections.",
                    "Continue activities and hobbies that you enjoy.",
                    "Maintain a balanced lifestyle with healthy eating and regular exercise."
                ]
            })
        else:
            interpretation.update({
                'level': 'Higher psychological distress',
                'description': "Your score indicates you might be experiencing a notable level of psychological distress. We strongly encourage you to seek support.",
                'suggestions': [
                    "Booking an appointment with a counselor is a highly recommended next step.",
                    "Please browse our Resources for articles and tools that can offer immediate coping strategies.",
                    "Talk to a trusted friend or family member about what you're experiencing."
                ],
                'show_urgent_suggestions': True,
                'linked_suggestions': [
                    {'text': 'Book an appointment with a counselor.', 'url_key': 'student_booking'},
                    {'text': 'Connect with peers on our anonymous forum.', 'url_key': 'student_forum'},
                    {'text': 'Explore our Wellness Journal to track your feelings.', 'url_key': 'student_journal'}
                ]
            })

    return interpretation

@app.before_request
def check_maintenance_mode():
    if request.path is None: return
    is_admin_request = request.path.startswith('/admin')
    # Add AI routes to essential endpoints to prevent maintenance block
    essential_endpoints = ['login_page', 'register_page', 'admin_register_page', 'login_validation', 'logout', 'add_user', 'add_admin', 'get_bot_response', 'voice_chat']
    is_essential_page = request.endpoint in essential_endpoints
    is_static = request.path.startswith('/static')
    if not is_admin_request and not is_essential_page and not is_static:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT setting_value FROM platform_settings WHERE setting_key = 'maintenance_mode'")
                    maintenance_mode = cursor.fetchone()
                    if maintenance_mode and maintenance_mode['setting_value'] == 'on':
                        return render_template("maintenance.html"), 503
            finally:
                conn.close()

# ---------------- Shared Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login_page(): return render_template("login.html")
@app.route("/register")
def register_page(): return render_template("register.html")
@app.route("/admin/register")
def admin_register_page(): return render_template("admin_register.html")

@app.route("/login_validation", methods=["POST"])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("password")
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('login_page'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session["user_id"] = user['id']
            session["user_role"] = user['role']
            session["username"] = user['username']
            session["is_volunteer"] = user.get('is_volunteer', 0)

            if user['role'] == "student":
                return redirect(url_for('student_dashboard'))
            elif user['role'] == "admin":
                return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()

    flash("Invalid email or password. Please try again.", "danger")
    return redirect(url_for('login_page'))

@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('register_page'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("An account with this email already exists.", "warning")
                return redirect(url_for('register_page'))

            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                         (name, email, hashed_password, "student"))
            
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            new_user = cursor.fetchone()

        session["user_id"] = new_user['id']
        session["user_role"] = new_user['role']
        session["username"] = new_user['username']
        session["is_volunteer"] = new_user.get('is_volunteer', 0)
        flash("Registration successful! You are now logged in.", "success")
        return redirect(url_for('student_dashboard'))
    finally:
        conn.close()


@app.route("/add_admin", methods=["POST"])
def add_admin():
    institute_name = request.form.get("institute_name")
    email = request.form.get("email")
    password = request.form.get("password")
    username = f"admin_{email}"
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('admin_register_page'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("An admin account with this email already exists.", "warning")
                return redirect(url_for('admin_register_page'))

            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, email, password, role, institute_name) VALUES (%s, %s, %s, %s, %s)",
                         (username, email, hashed_password, "admin", institute_name))
            
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            new_admin = cursor.fetchone()

        session["user_id"] = new_admin['id']
        session["user_role"] = new_admin['role']
        session["username"] = new_admin['username']
        flash("Institute registration successful! You are now logged in.", "success")
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('login_page'))

# ---------------- AI Chatbot Routes ----------------
def process_bot_response(response_text):
    """
    Processes the bot's response to replace url_for placeholders with actual URLs.
    """
    # This regex handles single or double curly braces and surrounding whitespace.
    pattern = r"\[(.*?)\]\s*\(\s*\{{1,2}\s*url_for\((.*?)\)\s*\}{1,2}\s*\)"
    
    def replace_link(match):
        link_text = match.group(1)
        endpoint_and_args = match.group(2).strip().replace("'", "").replace('"', '')
        parts = [p.strip() for p in endpoint_and_args.split(',')]
        endpoint = parts[0]
        kwargs = {}
        for part in parts[1:]:
            key, value = part.split('=')
            kwargs[key.strip()] = value.strip()
        
        try:
            with app.test_request_context():
                url = url_for(endpoint, **kwargs)
            return f'<a href="{url}" class="text-blue-600 hover:underline font-semibold" target="_blank">{link_text}</a>'
        except Exception as e:
            print(f"Error generating URL for '{link_text}': {e}")
            return link_text # Return text if URL generation fails

    return re.sub(pattern, replace_link, response_text)

@app.route("/get", methods=["POST"])
def get_bot_response():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_text = request.form.get('msg')
    session_id = request.form.get('sessionid')
    user_id = session['user_id']
    conn = get_db_connection()

    if not conn:
        return jsonify({"error": "Database connection error."}), 500
        
    try:
        with conn.cursor() as cursor:
            if not session_id or session_id == 'null' or session_id == 'undefined':
                session_id = str(uuid.uuid4())
                title = (user_text[:40] + '...') if len(user_text) > 40 else user_text
                cursor.execute("INSERT INTO chat_sessions (id, user_id, title) VALUES (%s, %s, %s)", (session_id, user_id, title))

            cursor.execute("INSERT INTO chat_history (session_id, user_id, sender, message) VALUES (%s, %s, 'user', %s)", (session_id, user_id, user_text))

            if detect_crisis(user_text):
                make_emergency_call()

            if not chain or not docsearch:
                error_message = "The AI Companion is not available due to a configuration error. Please check the server logs for details about API keys (GEMINI_API_KEY, PINECONE_API_KEY)."
                print(f"ERROR in /get: {error_message}")
                return jsonify({"error": error_message}), 500

            docs = docsearch.similarity_search(user_text, k=3)
            result = chain.invoke({"input_documents": docs, "question": user_text})
            bot_response = result['output_text']
            
            # Store the raw response from the bot
            cursor.execute("INSERT INTO chat_history (session_id, user_id, sender, message) VALUES (%s, %s, 'bot', %s)", (session_id, user_id, bot_response))

            # Process the response to convert placeholders to links before sending to frontend
            processed_response = process_bot_response(bot_response)
            
            return jsonify({"response": processed_response, "session_id": session_id})

    except Exception as e:
        print(f"An unexpected error occurred in get_bot_response: {e}")
        return jsonify({"error": "Sorry, an unexpected error occurred while contacting the AI. Please check the server logs."}), 500
    finally:
        conn.close()


# ---------------- Student Routes ----------------
@app.route("/student/chat")
@app.route("/student/chat/<session_id>")
def student_chat(session_id=None):
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return render_template("student/chat.html", chat_history=[], sessions=[], active_session_id=None)

    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            cursor.execute("SELECT id, title, created_at FROM chat_sessions WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            sessions = cursor.fetchall()

            chat_history = []
            active_session_id = session_id
            
            if active_session_id:
                cursor.execute("SELECT sender, message FROM chat_history WHERE user_id = %s AND session_id = %s ORDER BY created_at ASC", (user_id, active_session_id))
                chat_history_raw = cursor.fetchall()

                for row in chat_history_raw:
                    sender = row['sender']
                    if isinstance(sender, bytes):
                        sender = sender.decode('utf-8').strip()
                    else:
                        sender = str(sender).strip()

                    message = row['message']
                    if sender == 'bot':
                        # Process historical messages to convert placeholders to links
                        message = process_bot_response(message)
                    
                    chat_history.append({
                        'sender': sender,
                        'message': message
                    })

    finally:
        conn.close()
        
    return render_template("student/chat.html", chat_history=chat_history, sessions=sessions, active_session_id=active_session_id)


@app.route("/student/dashboard")
def student_dashboard():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    today = date.today()
    dashboard_data = {
        'tasks': [],
        'upcoming_appointment': None,
        'latest_mood': None
    }
    
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return render_template("student/dashboard.html", data=dashboard_data, **get_global_context())

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM daily_tasks WHERE user_id = %s AND task_date = %s", (user_id, today))
            tasks = cursor.fetchall()
            if not tasks:
                default_tasks = [
                    "Write in your Wellness Journal",
                    "Spend 5 minutes on a relaxation activity",
                    "Connect with a friend or family member",
                    "Get at least 15 minutes of physical activity",
                    "Review one helpful article from the Resources section"
                ]
                for task_desc in default_tasks:
                    cursor.execute(
                        "INSERT INTO daily_tasks (user_id, task_description, task_date) VALUES (%s, %s, %s)",
                        (user_id, task_desc, today)
                    )
                cursor.execute("SELECT * FROM daily_tasks WHERE user_id = %s AND task_date = %s", (user_id, today))
                tasks = cursor.fetchall()
            dashboard_data['tasks'] = tasks

            current_datetime = datetime.now()
            cursor.execute("""
                SELECT c.name as counselor_name, s.slot_date, s.start_time
                FROM appointments a
                JOIN counselors c ON a.counselor_id = c.id
                JOIN available_slots s ON a.slot_id = s.id
                WHERE a.user_id = %s AND (s.slot_date > %s OR (s.slot_date = %s AND s.start_time >= %s))
                ORDER BY s.slot_date, s.start_time
                LIMIT 1
            """, (user_id, current_datetime.date(), current_datetime.date(), current_datetime.time()))
            appointment = cursor.fetchone()
            if appointment and isinstance(appointment.get('start_time'), timedelta):
                total_seconds = int(appointment['start_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                appointment['start_time'] = dt_time(hours, minutes)
            dashboard_data['upcoming_appointment'] = appointment

            cursor.execute("SELECT mood FROM journal_entries WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
            mood_entry = cursor.fetchone()
            dashboard_data['latest_mood'] = mood_entry['mood'] if mood_entry else None

    finally:
        conn.close()
    
    context = get_global_context()
    return render_template("student/dashboard.html", data=dashboard_data, **context)

@app.route("/update_task_status", methods=['POST'])
def update_task_status():
    if "user_id" not in session or session.get("user_role") != "student":
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    task_id = data.get('task_id')
    is_completed = data.get('is_completed')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'Database connection error'}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE daily_tasks SET is_completed = %s WHERE id = %s AND user_id = %s",
                (is_completed, task_id, session['user_id'])
            )
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()


@app.route("/student/journal")
def student_journal():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database connection error"
    try:
        with conn.cursor() as cursor:
            user_id = session["user_id"]
            cursor.execute("SELECT * FROM journal_entries WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            entries = cursor.fetchall()
            
            mood_map = {'sad': 1, 'neutral': 2, 'okay': 3, 'happy': 4, 'great': 5}
            today = datetime.now()
            seven_days_ago = today - timedelta(days=6)
            
            cursor.execute("""
                SELECT DATE(created_at) as entry_date, mood FROM journal_entries 
                WHERE user_id = %s AND created_at >= %s
                ORDER BY created_at ASC
            """, (user_id, seven_days_ago))
            mood_data = cursor.fetchall()
    finally:
        conn.close()
    
    daily_moods = {}
    for record in mood_data:
        daily_moods[record['entry_date']] = mood_map.get(record['mood'], 0)

    chart_labels = []
    chart_data = []
    for i in range(7):
        day = seven_days_ago.date() + timedelta(days=i)
        chart_labels.append(day.strftime('%a'))
        chart_data.append(daily_moods.get(day))

    return render_template("student/journal.html", entries=entries, chart_labels=chart_labels, chart_data=chart_data)

@app.route("/add_journal_entry", methods=["POST"])
def add_journal_entry():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('student_journal'))
    try:
        with conn.cursor() as cursor:
            user_id = session["user_id"]
            entry_text = request.form.get("entry_text")
            mood = request.form.get("mood")

            if not entry_text or not mood:
                flash("Please fill out all fields.", "danger")
                return redirect(url_for('student_journal'))

            cursor.execute(
                "INSERT INTO journal_entries (user_id, entry_text, mood) VALUES (%s, %s, %s)",
                (user_id, entry_text, mood)
            )
        flash("Journal entry saved successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('student_journal'))

@app.route("/student/booking")
def student_booking():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database connection error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM counselors")
            all_counselors = cursor.fetchall()
            
            current_datetime = datetime.now()
            current_date = current_datetime.date()
            current_time_val = current_datetime.time()
            
            cursor.execute("""
                SELECT s.*, (SELECT COUNT(*) FROM appointments a WHERE a.slot_id = s.id) as booked_count
                FROM available_slots s
                WHERE s.slot_date > %s OR (s.slot_date = %s AND s.start_time > %s)
                ORDER BY s.slot_date, s.start_time
            """, (current_date, current_date, current_time_val))
            all_slots_raw = cursor.fetchall()
    finally:
        conn.close()

    all_slots = []
    for slot in all_slots_raw:
        if isinstance(slot.get('start_time'), timedelta):
            total_seconds = int(slot['start_time'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            slot['start_time'] = dt_time(hours, minutes)
        all_slots.append(slot)
    
    available_slots = [slot for slot in all_slots if slot['booked_count'] < slot['capacity']]
    
    return render_template("student/booking.html", counselors=all_counselors, slots=available_slots)

@app.route("/student/my_appointments")
def student_appointment_history():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database connection error."
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            cursor.execute("""
                SELECT a.id, c.name as counselor_name, s.slot_date, s.start_time
                FROM appointments a
                JOIN counselors c ON a.counselor_id = c.id
                JOIN available_slots s ON a.slot_id = s.id
                WHERE a.user_id = %s
                ORDER BY s.slot_date DESC, s.start_time DESC
            """, (user_id,))
            appointments_raw = cursor.fetchall()
    finally:
        conn.close()
        
    appointments = []
    for appt in appointments_raw:
        if isinstance(appt.get('start_time'), timedelta):
            total_seconds = int(appt['start_time'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            appt['start_time'] = dt_time(hours, minutes)
        appointments.append(appt)

    return render_template("student/appointment_history.html", appointments=appointments, current_time=datetime.now(), datetime=datetime)

@app.route("/book_appointment", methods=["POST"])
def book_appointment():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))

    student_id = session["user_id"]
    slot_id = request.form.get("slot_id")

    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('student_booking'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT capacity, (SELECT COUNT(*) FROM appointments WHERE slot_id = %s) as booked_count
                FROM available_slots WHERE id = %s
            """, (slot_id, slot_id))
            slot_info = cursor.fetchone()

            if not slot_info or slot_info['booked_count'] >= slot_info['capacity']:
                flash("Sorry, this slot is now full or no longer available.", "danger")
                return redirect(url_for('student_booking'))
            
            cursor.execute("SELECT id FROM appointments WHERE user_id = %s AND slot_id = %s", (student_id, slot_id))
            if cursor.fetchone():
                flash("You have already booked this appointment slot.", "warning")
                return redirect(url_for('student_booking'))

            cursor.execute("""
                INSERT INTO appointments (user_id, counselor_id, slot_id)
                SELECT %s, counselor_id, id FROM available_slots WHERE id = %s
            """, (student_id, slot_id))
            
        flash("Your appointment has been booked successfully!", "success")
    finally:
        conn.close()
    return redirect(url_for('student_appointment_history'))


@app.route("/student/resources")
def student_resources():
    if "user_id" in session and session.get("user_role") == "student":
        conn = get_db_connection()
        if not conn: return "Database error"
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM resources ORDER BY created_at DESC")
                all_resources = cursor.fetchall()
        finally:
            conn.close()
        return render_template("student/resources.html", resources=all_resources)
    return redirect(url_for('login_page'))

@app.route("/student/forum")
def student_forum():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
        
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.*, COUNT(fp.id) as post_count 
                FROM forum_topics t 
                LEFT JOIN forum_posts fp ON t.id = fp.topic_id 
                GROUP BY t.id 
                ORDER BY t.id
            """)
            topics = cursor.fetchall()
            
            cursor.execute("SELECT * FROM forum_guidelines")
            guidelines = cursor.fetchall()

            active_topic = request.args.get('topic_id', type=int)
            active_filter = request.args.get('filter')
            
            sql = """
                SELECT 
                    fp.id, fp.title, fp.created_at, u.username, fp.user_id, fp.status,
                    ft.name as topic_name,
                    (SELECT COUNT(*) FROM forum_replies fr WHERE fr.post_id = fp.id) as reply_count
                FROM forum_posts fp 
                JOIN users u ON fp.user_id = u.id
                JOIN forum_topics ft ON fp.topic_id = ft.id
            """
            params = []
            where_clauses = []

            if active_topic:
                where_clauses.append("fp.topic_id = %s")
                params.append(active_topic)
            
            if active_filter == 'my_discussions':
                where_clauses.append("fp.user_id = %s")
                params.append(session['user_id'])
            elif active_filter == 'other_discussions':
                 where_clauses.append("fp.user_id != %s")
                 params.append(session['user_id'])

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " ORDER BY fp.created_at DESC"
            
            cursor.execute(sql, tuple(params))
            posts = cursor.fetchall()
    finally:
        conn.close()
        
    context = get_global_context()
    return render_template("student/forum.html", posts=posts, topics=topics, guidelines=guidelines, 
                           active_topic=active_topic, active_filter=active_filter, **context)

@app.route("/student/add_post", methods=['POST'])
def add_post():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: 
        flash("Database error", "danger")
        return redirect(url_for('student_forum'))
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            title = request.form.get('title')
            content = request.form.get('content')
            topic_id = request.form.get('topic_id')

            if not all([title, content, topic_id]):
                flash("Title, content, and topic are required.", "danger")
                return redirect(url_for('student_forum'))

            cursor.execute("INSERT INTO forum_posts (user_id, title, content, topic_id) VALUES (%s, %s, %s, %s)",(user_id, title, content, topic_id))
        flash("Your discussion has been posted!", "success")
    finally:
        conn.close()
    return redirect(url_for('student_forum'))

@app.route('/student/discussion/<int:post_id>')
def student_discussion(post_id):
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT fp.*, u.username, ft.name as topic_name 
                FROM forum_posts fp 
                JOIN users u ON fp.user_id = u.id 
                JOIN forum_topics ft ON fp.topic_id = ft.id
                WHERE fp.id = %s
            """,(post_id,))
            post = cursor.fetchone()

            if not post:
                flash("Post not found.", "danger")
                return redirect(url_for('student_forum'))
                
            cursor.execute("""
                SELECT fr.*, u.username, u.is_volunteer, fr.user_id 
                FROM forum_replies fr 
                JOIN users u ON fr.user_id = u.id 
                WHERE fr.post_id = %s 
                ORDER BY fr.created_at ASC
            """,(post_id,))
            replies = cursor.fetchall()
    finally:
        conn.close()
    
    context = get_global_context()
    return render_template('student/discussion.html', post=post, replies=replies, **context)

@app.route('/student/resolve_discussion/<int:post_id>', methods=['POST'])
def resolve_discussion(post_id):
    if "user_id" not in session:
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for('student_discussion', post_id=post_id))

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM forum_posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()
            if not post:
                flash("Post not found.", "danger")
                return redirect(url_for('student_forum'))
            
            if session['user_id'] == post['user_id'] or session.get('is_volunteer'):
                cursor.execute("UPDATE forum_posts SET status = 'resolved' WHERE id = %s", (post_id,))
                flash("Discussion has been marked as resolved.", "success")
            else:
                flash("You do not have permission to perform this action.", "danger")
    finally:
        conn.close()

    return redirect(url_for('student_discussion', post_id=post_id))

@app.route('/student/add_reply', methods=['POST'])
def add_reply():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    post_id = request.form.get('post_id')
    if not session.get('is_volunteer'):
        flash("Only trained student volunteers can reply to discussions.", "warning")
        return redirect(url_for('student_discussion', post_id=post_id))
    
    conn = get_db_connection()
    if not conn: 
        flash("Database error", "danger")
        return redirect(url_for('student_discussion', post_id=post_id))
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            content = request.form.get('content')

            if not content:
                flash("Reply content cannot be empty.", "danger")
                return redirect(url_for('student_discussion', post_id=post_id))

            cursor.execute("INSERT INTO forum_replies (post_id, user_id, content) VALUES (%s, %s, %s)",(post_id, user_id, content))
        flash("Your reply has been posted.", "success")
    finally:
        conn.close()
    return redirect(url_for('student_discussion', post_id=post_id))

@app.route('/student/report_content', methods=['POST'])
def report_content():
    if "user_id" not in session:
        return redirect(url_for('login_page'))

    post_id = None
    reply_id = None
    report_type = request.form.get('report_type')
    content_id = request.form.get('content_id')
    if report_type == 'post':
        post_id = content_id
    else:
        reply_id = content_id

    reported_user_id = request.form.get('reported_user_id')
    reason = request.form.get('reason')
    reported_by_user_id = session['user_id']

    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
    else:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO forum_reports (post_id, reply_id, reported_user_id, reported_by_user_id, reason)
                    VALUES (%s, %s, %s, %s, %s)
                """, (post_id, reply_id, reported_user_id, reported_by_user_id, reason))
            flash("Content has been reported for review. Thank you.", "success")
        finally:
            conn.close()
    
    return redirect(request.referrer or url_for('student_forum'))

@app.route('/student/submit_volunteer_feedback', methods=['POST'])
def submit_volunteer_feedback():
    if "user_id" not in session:
        return redirect(url_for('login_page'))

    volunteer_user_id = request.form.get('volunteer_user_id')
    post_id = request.form.get('post_id')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    feedback_by_user_id = session['user_id']
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
    else:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO volunteer_feedback (volunteer_user_id, feedback_by_user_id, post_id, rating, comment)
                    VALUES (%s, %s, %s, %s, %s)
                """, (volunteer_user_id, feedback_by_user_id, post_id, rating, comment))
            flash("Thank you for your feedback!", "success")
        finally:
            conn.close()
    
    return redirect(url_for('student_discussion', post_id=post_id))

@app.route("/student/facial-expression")
def student_facial_expression():
    if "user_id" in session and session.get("user_role") == "student":
        user_id = session['user_id']
        history = get_emotion_history(user_id)
        
        # Prepare data for Chart.js
        labels = [h['log_date'].strftime('%b %d') for h in history]
        emotions = ["neutral", "happy", "surprise", "angry", "disgust", "fear", "sad"]
        
        datasets = {emotion: [h[emotion] for h in history] for emotion in emotions}

        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        return render_template("student/facial-expression.html", chart_data=chart_data)
    return redirect(url_for('login_page'))

# FIX: Pass user_id as an argument to decouple from request context
def generate_frames(user_id):
    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    last_saved_time = time.time()

    if not user_id:
        print("User not logged in, cannot save emotion data.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Detect emotion and get the processed frame
            processed_frame, emotions = detect_emotion(frame)

            # Save data to the database every 5 seconds if any emotion is detected
            if (time.time() - last_saved_time > 5) and any(emotions.values()):
                print(f"Logging emotions for user {user_id}: {emotions}")
                save_emotion_log(user_id, emotions)
                last_saved_time = time.time()
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            # Yield the frame in the correct format for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

@app.route('/video_feed')
def video_feed():
    if "user_id" not in session or session.get("user_role") != "student":
        return "Unauthorized", 401
    
    # FIX: Get user_id from session here and pass it to the generator
    user_id = session['user_id']
    return Response(generate_frames(user_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/student/activities")
def student_activities():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM activities")
            activities = cursor.fetchall()
            user_id = session["user_id"]
            cursor.execute("SELECT game_name, score FROM game_scores WHERE user_id = %s", (user_id,))
            scores_data = cursor.fetchall()
    finally:
        conn.close()

    high_scores = {item['game_name']: item['score'] for item in scores_data}
    return render_template("student/activities.html", activities=activities, high_scores=high_scores)

@app.route("/student/activity/<activity_name>")
def student_activity_view(activity_name):
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM activities WHERE name = %s", (activity_name,))
            activity_info = cursor.fetchone()

            if not activity_info:
                flash("Activity not found.", "danger")
                return redirect(url_for('student_activities'))
            
            high_score = 0
            if activity_info['type'] == 'Game':
                user_id = session["user_id"]
                cursor.execute("SELECT score FROM game_scores WHERE user_id = %s AND game_name = %s", (user_id, activity_name))
                score_data = cursor.fetchone()
                high_score = score_data['score'] if score_data else 0
    finally:
        conn.close()

    return render_template("student/activity_view.html", activity=activity_info, high_score=high_score)

@app.route("/save_score", methods=['POST'])
def save_score():
    if "user_id" not in session or session.get("user_role") != "student":
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'Database connection error'}), 500
    try:
        with conn.cursor() as cursor:
            data = request.json
            user_id = session['user_id']
            game_name = data.get('game_name')
            new_score = int(data.get('score', 0))

            cursor.execute("SELECT name FROM activities WHERE name = %s AND type = 'Game'", (game_name,))
            if not cursor.fetchone():
                 return jsonify({'status': 'error', 'message': 'Invalid game'}), 400

            cursor.execute("SELECT score FROM game_scores WHERE user_id = %s AND game_name = %s", (user_id, game_name))
            current_score_data = cursor.fetchone()
            current_high_score = current_score_data['score'] if current_score_data else 0

            if new_score > current_high_score:
                cursor.execute("""
                    INSERT INTO game_scores (user_id, game_name, score) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE score = %s
                """, (user_id, game_name, new_score, new_score))
                return jsonify({'status': 'success', 'message': 'New high score saved!'})
    finally:
        conn.close()
    return jsonify({'status': 'success', 'message': 'Score not higher than current best.'})

# ----------------- Assessment Routes -----------------
@app.route("/student/assessments")
def student_assessments():
    if "user_id" in session and session.get("user_role") == "student":
        return render_template("student/assessments.html")
    return redirect(url_for('login_page'))

@app.route("/student/assessment/<assessment_name>")
def student_assessment(assessment_name):
    if "user_id" in session and session.get("user_role") == "student":
        if assessment_name == "phq9":
            return render_template("student/phq9.html")
        elif assessment_name == "gad7":
            return render_template("student/gad7.html")
        elif assessment_name == "ghq12":
            return render_template("student/ghq12.html")
    return redirect(url_for('login_page'))

@app.route("/student/save_assessment", methods=['POST'])
def save_assessment():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('student_assessments'))
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            assessment_type = request.form.get('assessment_type')
            
            score = 0
            for key, value in request.form.items():
                if key.startswith('q'):
                    score += int(value)

            cursor.execute(
                "INSERT INTO assessment_scores (user_id, assessment_type, score) VALUES (%s, %s, %s)",
                (user_id, assessment_type, score)
            )
        
        interpretation_data = get_assessment_interpretation(assessment_type, score)

    finally:
        conn.close()
    
    return render_template(
        "student/assessment_result.html",
        score=score,
        assessment_type=assessment_type,
        interpretation=interpretation_data
    )

@app.route("/student/assessment_history")
def student_assessment_history():
    if "user_id" not in session or session.get("user_role") != "student":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database connection error."
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            cursor.execute("SELECT * FROM assessment_scores WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            history = cursor.fetchall()
            
            # Fetch data for charts
            cursor.execute("SELECT score, created_at FROM assessment_scores WHERE user_id = %s AND assessment_type = 'PHQ-9' ORDER BY created_at ASC", (user_id,))
            phq9_data = cursor.fetchall()
            
            cursor.execute("SELECT score, created_at FROM assessment_scores WHERE user_id = %s AND assessment_type = 'GAD-7' ORDER BY created_at ASC", (user_id,))
            gad7_data = cursor.fetchall()

            cursor.execute("SELECT score, created_at FROM assessment_scores WHERE user_id = %s AND assessment_type = 'GHQ-12' ORDER BY created_at ASC", (user_id,))
            ghq12_data = cursor.fetchall()
    finally:
        conn.close()

    chart_data = {
        'phq9': {
            'labels': [d['created_at'].strftime('%b %d') for d in phq9_data],
            'scores': [d['score'] for d in phq9_data]
        },
        'gad7': {
            'labels': [d['created_at'].strftime('%b %d') for d in gad7_data],
            'scores': [d['score'] for d in gad7_data]
        },
        'ghq12': {
            'labels': [d['created_at'].strftime('%b %d') for d in ghq12_data],
            'scores': [d['score'] for d in ghq12_data]
        }
    }

    return render_template("student/assessment_history.html", history=history, chart_data=chart_data)

@app.route("/student/report_bug", methods=['POST'])
def report_bug():
    if "user_id" not in session or session.get("user_role") != "student":
        flash("You must be logged in to report a bug.", "warning")
        return redirect(request.referrer or url_for('student_dashboard'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error. Could not submit report.", "danger")
        return redirect(request.referrer or url_for('student_dashboard'))
    try:
        with conn.cursor() as cursor:
            user_id = session['user_id']
            reporter_name = request.form.get('reporter_name')
            description = request.form.get('report_description')

            if not description:
                flash("Please provide a description of the bug.", "danger")
                return redirect(request.referrer or url_for('student_dashboard'))

            cursor.execute(
                "INSERT INTO bug_reports (user_id, reporter_name, report_description) VALUES (%s, %s, %s)",
                (user_id, reporter_name, description)
            )
        flash("Thank you! Your bug report has been submitted.", "success")
    finally:
        conn.close()
    return redirect(request.referrer or url_for('student_dashboard'))


# ---------------- Admin Routes ----------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
            total_students = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM appointments")
            total_appointments = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM resources")
            total_resources = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM forum_posts")
            total_forum_posts = cursor.fetchone()['count']
            stats = {'total_students': total_students, 'total_appointments': total_appointments, 'total_resources': total_resources, 'total_forum_posts': total_forum_posts}
            
            cursor.execute("SELECT username, email, created_at FROM users WHERE role = 'student' ORDER BY created_at DESC LIMIT 5")
            recent_students = cursor.fetchall()
            
            cursor.execute("""SELECT fp.id, fp.title, fp.created_at, u.username FROM forum_posts fp JOIN users u ON fp.user_id = u.id ORDER BY fp.created_at DESC LIMIT 5""")
            recent_posts = cursor.fetchall()

            mood_labels = ['Sad', 'Neutral', 'Okay', 'Happy', 'Great']
            cursor.execute("""SELECT mood, COUNT(*) as count FROM journal_entries GROUP BY mood ORDER BY FIELD(mood, 'sad', 'neutral', 'okay', 'happy', 'great')""")
            mood_data_raw = cursor.fetchall()
    finally:
        conn.close()

    mood_counts = {item['mood']: item['count'] for item in mood_data_raw}
    mood_chart_data = [mood_counts.get(mood.lower(), 0) for mood in mood_labels]

    return render_template("admin/dashboard.html", stats=stats, recent_students=recent_students, recent_posts=recent_posts, mood_labels=mood_labels, mood_chart_data=mood_chart_data)

@app.route("/admin/users")
def admin_users():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            search_query = request.args.get('search', '')
            sort_by = request.args.get('sort', 'name_asc')
            base_query = "SELECT id, username, email, created_at, is_volunteer FROM users WHERE role = 'student'"
            params = []
            if search_query:
                base_query += " AND (username LIKE %s OR email LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])
            sort_options = {'name_asc': ' ORDER BY username ASC', 'name_desc': ' ORDER BY username DESC', 'date_asc': ' ORDER BY created_at ASC', 'date_desc': ' ORDER BY created_at DESC'}
            base_query += sort_options.get(sort_by, ' ORDER BY username ASC')
            cursor.execute(base_query, tuple(params))
            students = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template("admin/users.html", students=students, search_query=search_query, sort_by=sort_by)

@app.route('/admin/toggle_volunteer/<int:user_id>')
def toggle_volunteer(user_id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_users'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_volunteer = NOT is_volunteer WHERE id = %s AND role = 'student'", (user_id,))
        flash("User's volunteer status has been updated.", "success")
    finally:
        conn.close()
    
    if request.args.get('next') == 'volunteers':
        return redirect(url_for('admin_volunteers'))
    return redirect(url_for('admin_users'))

@app.route('/admin/volunteers')
def admin_volunteers():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE role = 'student' AND is_volunteer = 1")
            volunteers = cursor.fetchall()
            
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE role = 'student' AND is_volunteer = 0")
            students = cursor.fetchall()

            cursor.execute("""
                SELECT 
                    vf.*, 
                    v.username as volunteer_name, 
                    fbu.username as feedback_by_username
                FROM volunteer_feedback vf
                JOIN users v ON vf.volunteer_user_id = v.id
                JOIN users fbu ON vf.feedback_by_user_id = fbu.id
                ORDER BY vf.created_at DESC
            """)
            all_feedback = cursor.fetchall()

            cursor.execute("""
                SELECT volunteer_user_id, AVG(rating) as avg_rating, COUNT(id) as count
                FROM volunteer_feedback
                GROUP BY volunteer_user_id
            """)
            feedback_summary = cursor.fetchall()
            
    finally:
        conn.close()

    volunteer_feedback_stats = {item['volunteer_user_id']: item for item in feedback_summary}

    return render_template("admin/volunteers.html", volunteers=volunteers, students=students, all_feedback=all_feedback, volunteer_feedback=volunteer_feedback_stats)

@app.route("/admin/resources")
def admin_resources():
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn: return "Database error"
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM resources ORDER BY id DESC")
                all_resources = cursor.fetchall()
        finally:
            conn.close()
        return render_template("admin/resources.html", resources=all_resources)
    return redirect(url_for('login_page'))

@app.route("/admin/add_resource", methods=['POST'])
def add_resource():
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn: 
            flash("Database error", "danger")
            return redirect(url_for('admin_resources'))
        try:
            with conn.cursor() as cursor:
                title = request.form.get('title')
                description = request.form.get('description')
                resource_type = request.form.get('resource_type')
                link = request.form.get('link')
                image_url = request.form.get('image_url')
                content = request.form.get('content')
                cursor.execute("INSERT INTO resources (title, description, resource_type, link, image_url, content) VALUES (%s, %s, %s, %s, %s, %s)",
                             (title, description, resource_type, link, image_url, content))
            flash('Resource added successfully!', 'success')
        finally:
            conn.close()
    return redirect(url_for('admin_resources'))

@app.route('/admin/delete_resource/<int:resource_id>')
def delete_resource(resource_id):
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn:
            flash("Database error", "danger")
            return redirect(url_for('admin_resources'))
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM resources WHERE id = %s", (resource_id,))
            flash('Resource deleted successfully.', 'danger')
        finally:
            conn.close()
    return redirect(url_for('admin_resources'))

@app.route("/admin/appointments")
def admin_appointments():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM counselors")
            all_counselors = cursor.fetchall()
            cursor.execute("""SELECT s.*, (SELECT COUNT(*) FROM appointments a WHERE a.slot_id = s.id) as booked_count FROM available_slots s ORDER BY s.slot_date, s.start_time""")
            all_slots_raw = cursor.fetchall()
            cursor.execute("""SELECT a.id, u.username, c.name as counselor_name, s.slot_date, s.start_time FROM appointments a JOIN users u ON a.user_id = u.id JOIN available_slots s ON a.slot_id = s.id JOIN counselors c ON s.counselor_id = c.id ORDER BY s.slot_date, s.start_time""")
            booked_appointments_raw = cursor.fetchall()
    finally:
        conn.close()

    all_slots = []
    for slot in all_slots_raw:
        if isinstance(slot.get('start_time'), timedelta):
            total_seconds = int(slot['start_time'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            slot['start_time'] = dt_time(hours, minutes)
        all_slots.append(slot)

    booked_appointments = []
    for appt in booked_appointments_raw:
        if isinstance(appt.get('start_time'), timedelta):
            total_seconds = int(appt['start_time'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            appt['start_time'] = dt_time(hours, minutes)
        booked_appointments.append(appt)

    return render_template("admin/appointments.html", counselors=all_counselors, slots=all_slots, booked_appointments=booked_appointments)

@app.route("/admin/add_counselor", methods=["POST"])
def add_counselor():
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn:
            flash("Database error", "danger")
            return redirect(url_for('admin_appointments'))
        try:
            with conn.cursor() as cursor:
                name = request.form.get("name")
                specialty = request.form.get("specialty")
                image_url = request.form.get("image_url")
                cursor.execute(
                    "INSERT INTO counselors (name, specialty, image_url) VALUES (%s, %s, %s)",
                    (name, specialty, image_url)
                )
            flash("Counselor added successfully.", "success")
        except pymysql.Error as e:
            flash(f"Database error: {e}", "danger")
        finally:
            if conn:
                conn.close()
    return redirect(url_for('admin_appointments'))

@app.route("/admin/remove_counselor/<int:counselor_id>")
def remove_counselor(counselor_id):
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn:
            flash("Database error", "danger")
            return redirect(url_for('admin_appointments'))
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM counselors WHERE id=%s", (counselor_id,))
            flash("Counselor removed successfully.", "danger")
        finally:
            conn.close()
    return redirect(url_for('admin_appointments'))

@app.route("/admin/add_slot", methods=["POST"])
def add_slot():
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn:
            flash("Database error", "danger")
            return redirect(url_for('admin_appointments'))
        try:
            with conn.cursor() as cursor:
                counselor_id = request.form.get("counselor_id")
                slot_date = request.form.get("slot_date")
                start_time = request.form.get("start_time")
                capacity = request.form.get("capacity", 1, type=int)
                cursor.execute("INSERT INTO available_slots (counselor_id, slot_date, start_time, capacity) VALUES (%s, %s, %s, %s)",
                             (counselor_id, slot_date, start_time, capacity))
            flash("Time slot added successfully.", "success")
        finally:
            conn.close()
    return redirect(url_for('admin_appointments'))

@app.route("/admin/delete_slot/<int:slot_id>")
def delete_slot(slot_id):
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn:
            flash("Database error", "danger")
            return redirect(url_for('admin_appointments'))
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM available_slots WHERE id = %s", (slot_id,))
            flash("Slot deleted successfully.", "danger")
        finally:
            conn.close()
    return redirect(url_for('admin_appointments'))

@app.route("/admin/forum")
def admin_forum():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
        
    conn = get_db_connection()
    if not conn: 
        flash("Database error", "danger")
        return redirect(url_for('admin_dashboard'))
    try:
        with conn.cursor() as cursor:
            active_filter = request.args.get('filter', 'all')
            
            cursor.execute("""
                SELECT 
                    fr.id, fr.reason, fr.created_at, fr.post_id, fr.reply_id,
                    reporter.username as reporter_username,
                    reported.username as reported_username,
                    (SELECT post_id from forum_replies where id = fr.reply_id) as reply_post_id
                FROM forum_reports fr
                JOIN users reporter ON fr.reported_by_user_id = reporter.id
                JOIN users reported ON fr.reported_user_id = reported.id
                WHERE fr.status = 'pending'
                ORDER BY fr.created_at DESC
            """)
            reports = cursor.fetchall()
            
            post_sql = "SELECT fp.id, fp.title, fp.status, fp.created_at, u.username FROM forum_posts fp JOIN users u ON fp.user_id = u.id"
            if active_filter == 'open':
                post_sql += " WHERE fp.status = 'open'"
            elif active_filter == 'resolved':
                post_sql += " WHERE fp.status = 'resolved'"
            
            post_sql += " ORDER BY fp.created_at DESC"
            cursor.execute(post_sql)
            posts = cursor.fetchall()

    finally:
        conn.close()
        
    return render_template("admin/forum.html", posts=posts, reports=reports, active_filter=active_filter)

@app.route('/admin/delete_post/<int:post_id>')
def delete_post(post_id):
    if "user_id" in session and session.get("user_role") == "admin":
        conn = get_db_connection()
        if not conn:
            flash("Database error", "danger")
            return redirect(url_for('admin_forum'))
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM forum_posts WHERE id = %s", (post_id,))
            flash("Post has been deleted successfully.", "success")
        finally:
            conn.close()
    return redirect(url_for('admin_forum'))
    
@app.route('/admin/resolve_report/<int:report_id>')
def resolve_report(report_id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_forum'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE forum_reports SET status = 'resolved' WHERE id = %s", (report_id,))
        flash("Report has been marked as resolved.", "success")
    finally:
        conn.close()
    return redirect(url_for('admin_forum', filter='reports'))

@app.route('/admin/activities')
def admin_activities():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn: return "Database error"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM activities ORDER BY type, title")
            all_activities = cursor.fetchall()
    finally:
        conn.close()
    return render_template('admin/activities.html', activities=all_activities)

@app.route('/admin/add_activity', methods=['POST'])
def add_activity():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_activities'))
    try:
        with conn.cursor() as cursor:
            name = request.form.get('name')
            title = request.form.get('title')
            act_type = request.form.get('type')
            description = request.form.get('description')
            embed_url = request.form.get('embed_url')
            image_url = request.form.get('image_url')

            if not all([name, title, act_type, description, embed_url]):
                flash("All fields except Image URL are required.", "danger")
                return redirect(url_for('admin_activities'))

            try:
                cursor.execute("INSERT INTO activities (name, title, type, description, embed_url, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                             (name, title, act_type, description, embed_url, image_url))
                flash("Activity added successfully!", "success")
            except pymysql.IntegrityError:
                flash("An activity with this 'Name (Unique ID)' already exists.", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_activities'))

@app.route('/admin/edit_activity/<int:activity_id>', methods=['GET', 'POST'])
def edit_activity(activity_id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))

    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_activities'))
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                name = request.form.get('name')
                title = request.form.get('title')
                act_type = request.form.get('type')
                description = request.form.get('description')
                embed_url = request.form.get('embed_url')
                image_url = request.form.get('image_url')
                if not all([name, title, act_type, description, embed_url]):
                    flash("All fields except Image URL are required.", "danger")
                    return redirect(url_for('edit_activity', activity_id=activity_id))
                cursor.execute("""UPDATE activities SET name = %s, title = %s, type = %s, description = %s, embed_url = %s, image_url = %s WHERE id = %s""",
                             (name, title, act_type, description, embed_url, image_url, activity_id))
                flash('Activity updated successfully!', 'success')
                return redirect(url_for('admin_activities'))

            cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
            activity = cursor.fetchone()
            if not activity:
                flash('Activity not found.', 'danger')
                return redirect(url_for('admin_activities'))
    finally:
        conn.close()
    return render_template('admin/edit_activity.html', activity=activity)

@app.route('/admin/delete_activity/<int:activity_id>')
def delete_activity(activity_id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_activities'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM activities WHERE id = %s", (activity_id,))
        flash("Activity deleted successfully.", "success")
    finally:
        conn.close()
    return redirect(url_for('admin_activities'))

@app.route("/admin/settings", methods=['GET', 'POST'])
def admin_settings():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_dashboard'))
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                settings_to_update = {
                    'emergency_contact_name': request.form.get('emergency_contact_name', ''),
                    'emergency_contact_number': request.form.get('emergency_contact_number', ''),
                    'welcome_message': request.form.get('welcome_message', ''),
                    'forum_anonymity': request.form.get('forum_anonymity', 'anonymous'),
                    'maintenance_mode': 'on' if 'maintenance_mode' in request.form else 'off'
                }
                for key, value in settings_to_update.items():
                    cursor.execute("""INSERT INTO platform_settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value = %s""",
                                 (key, value, value))
                flash("Settings updated successfully!", "success")
                return redirect(url_for('admin_settings'))

            cursor.execute("SELECT setting_key, setting_value FROM platform_settings")
            settings_data = cursor.fetchall()
            settings = {item['setting_key']: item['setting_value'] for item in settings_data}
    finally:
        conn.close()
    return render_template("admin/settings.html", settings=settings)

@app.route("/admin/bug_reports")
def admin_bug_reports():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_dashboard'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM bug_reports ORDER BY report_date DESC")
            reports = cursor.fetchall()
    finally:
        conn.close()
    return render_template("admin/bug_reports.html", reports=reports)

@app.route('/admin/resolve_bug/<int:report_id>')
def resolve_bug(report_id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for('login_page'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database error", "danger")
        return redirect(url_for('admin_bug_reports'))
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE bug_reports SET is_resolved = 1 WHERE id = %s", (report_id,))
        flash("Bug report has been marked as resolved.", "success")
    finally:
        conn.close()
    return redirect(url_for('admin_bug_reports'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
