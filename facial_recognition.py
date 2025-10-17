import os

# Suppress TensorFlow INFO and WARNING logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import pymysql
import pymysql.cursors
from datetime import datetime

# --- Model and Cascade Paths ---
# IMPORTANT: Download these files and place them in the root of your project.
# Haar Cascade for face detection: https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
# A pre-trained emotion model (H5 file) trained on FER2013 dataset. You can find one on Kaggle or GitHub.

FACE_CASCADE_PATH = 'haarcascade_frontalface_default.xml'
EMOTION_MODEL_PATH = 'emotion_model.h5'

# --- Emotion Labels ---
EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

# --- Global variables for the models ---
face_cascade = None
emotion_model = None

def load_models():
    """Loads the face cascade and emotion model into memory."""
    global face_cascade, emotion_model
    
    if face_cascade is None:
        face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
    
    if emotion_model is None:
        try:
            # Try loading with compilation first
            emotion_model = load_model(EMOTION_MODEL_PATH)
        except ValueError as e:
            if "lr" in str(e) or "Argument(s) not recognized" in str(e):
                # Load without compilation for compatibility with older models
                print("Loading model without optimizer compilation for compatibility...")
                emotion_model = load_model(EMOTION_MODEL_PATH, compile=False)
            else:
                raise e

def detect_emotion(frame):
    """
    Detects faces in a frame, predicts their emotion, and draws on the frame.
    Returns the frame and a dictionary of detected emotions.
    """
    if face_cascade is None or emotion_model is None:
        load_models()
    
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    
    detected_emotions = {emotion: 0 for emotion in EMOTIONS}
    
    for (x, y, w, h) in faces:
        # Extract the region of interest (ROI)
        roi_gray = gray_frame[y:y + h, x:x + w]
        # Resize to 64x64 to match model's expected input shape
        roi_gray = cv2.resize(roi_gray, (64, 64))
        roi = roi_gray.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        
        # Predict the emotion
        preds = emotion_model.predict(roi)[0]
        label = EMOTIONS[preds.argmax()]
        
        # Increment the count for the detected emotion
        if label in detected_emotions:
            detected_emotions[label] += 1
        
        # Draw bounding box and label on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
    
    return frame, detected_emotions

def get_db_connection_local():
    """Establishes a local database connection for this module."""
    try:
        return pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "0000"),
            database=os.getenv("DB_NAME", "udaan_db"),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    except pymysql.Error as e:
        print(f"Database connection error in facial_recognition module: {e}")
        return None

def save_emotion_log(user_id, emotions):
    """Saves the detected emotion counts to the database."""
    conn = get_db_connection_local()
    if not conn or not any(emotions.values()):
        return
    
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO emotion_logs 
            (user_id, neutral, happy, surprise, angry, disgust, fear, sad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_id,
                emotions.get("Neutral", 0),
                emotions.get("Happy", 0),
                emotions.get("Surprise", 0),
                emotions.get("Angry", 0),
                emotions.get("Disgust", 0),
                emotions.get("Fear", 0),
                emotions.get("Sad", 0)
            ))
    except pymysql.Error as e:
        print(f"Error saving emotion log: {e}")
    finally:
        if conn:
            conn.close()

def get_emotion_history(user_id):
    """Fetches and aggregates emotion data for a user."""
    conn = get_db_connection_local()
    if not conn:
        return {}
    
    try:
        with conn.cursor() as cursor:
            # Fetch data from the last 30 days, aggregated by day
            sql = """
            SELECT 
                DATE(log_time) as log_date,
                SUM(neutral) as neutral, SUM(happy) as happy, SUM(surprise) as surprise,
                SUM(angry) as angry, SUM(disgust) as disgust, SUM(fear) as fear, SUM(sad) as sad
            FROM emotion_logs 
            WHERE user_id = %s AND log_time >= CURDATE() - INTERVAL 30 DAY
            GROUP BY DATE(log_time)
            ORDER BY log_date ASC
            """
            cursor.execute(sql, (user_id,))
            history = cursor.fetchall()
            return history
    except pymysql.Error as e:
        print(f"Error fetching emotion history: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_models()  # load Haar cascade + emotion model
    cap = cv2.VideoCapture(0)  # open default camera
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect emotions
        frame, emotions = detect_emotion(frame)
        
        # Show live video with detections
        cv2.imshow("Emotion Detection", frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
