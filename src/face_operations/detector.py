import cv2
import os
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import time
import logging

# Configure logging (ensure it's configured only once)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables to hold loaded models (to avoid reloading)
knn_model = None
label_map = None
age_model = None
face_cascade = None

def load_models(models_dir):
    global knn_model, label_map, age_model, face_cascade
    models_loaded = True
    logging.info("Loading models...")

    # Load face recognition model
    if knn_model is None or label_map is None:
        try:
            recog_model_path = os.path.join(models_dir, "face_recognition_model.pkl")
            label_map_path = os.path.join(models_dir, "label_map.pkl")
            with open(recog_model_path, "rb") as f:
                knn_model = pickle.load(f)
            with open(label_map_path, "rb") as f:
                label_map = pickle.load(f)
            logging.info("Face recognition model loaded.")
        except FileNotFoundError:
            logging.error(f"Face model files not found in {models_dir}")
            models_loaded = False
        except Exception as e:
            logging.error(f"Error loading face model: {e}")
            models_loaded = False

    # Load age prediction model
    if age_model is None:
        try:
            age_model_path = os.path.join(models_dir, "age_model.h5")
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            os.environ['KMP_DUPLICATE_LIB_OK']='True'
            age_model = load_model(age_model_path, compile=False)
            logging.info("Age prediction model loaded.")
        except Exception as e:
            logging.error(f"Error loading age model ({age_model_path}): {e}")
            models_loaded = False

    # Load face cascade
    if face_cascade is None:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            logging.error(f"Haar cascade file not found at {cascade_path}")
            models_loaded = False
        else:
            face_cascade = cv2.CascadeClassifier(cascade_path)
            logging.info("Face cascade loaded.")

    return models_loaded

def predict_face(frame):
    global knn_model, label_map, face_cascade
    if frame is None or knn_model is None or label_map is None or face_cascade is None:
        logging.warning("Predict face called before models loaded or with None frame.")
        return None, None # Return None for name and coordinates if error

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) == 0:
        return "No face", None # No face detected

    # Find the largest face
    (x, y, w, h) = max(faces, key=lambda item: item[2] * item[3])
    face_coords = (x, y, w, h)

    # Recognize
    try:
        face_image_gray = gray[y:y + h, x:x + w]
        face_resized_gray = cv2.resize(face_image_gray, (100, 100)).flatten().reshape(1, -1)
        label_pred = knn_model.predict(face_resized_gray)[0]
        name = label_map.get(label_pred, "Unknown")
        logging.debug(f"Face recognized: {name}")
        return name, face_coords
    except Exception as e:
        logging.warning(f"Error during face recognition prediction: {e}")
        return "Error", face_coords # Return error status and coords

def predict_age(frame, face_coords):
    global age_model
    if frame is None or face_coords is None or age_model is None:
        logging.warning("Predict age called with invalid args or model not loaded.")
        return -1 # Return -1 for invalid age

    (x, y, w, h) = face_coords
    if w <= 0 or h <= 0:
        return -1 # Invalid coordinates

    try:
        face_rgb = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2RGB)
        face_for_age = cv2.resize(face_rgb, (224, 224)) / 255.0
        face_for_age = np.expand_dims(face_for_age, axis=0)
        predicted_age = int(age_model.predict(face_for_age, verbose=0)[0][0])
        logging.debug(f"Age predicted: {predicted_age}")
        return predicted_age
    except Exception as e:
        logging.warning(f"Error during age prediction: {e}")
        return -1 # Return -1 on error

# --- Kept for potential direct testing, but main logic moved to main.py Worker --- 
# def check_user_age(duration_seconds=5):
#     if not load_models():
#         return False, -1
#
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         logging.error("Cannot open webcam.")
#         return False, -1
#     logging.info("Webcam opened successfully.")
#
#     age_predictions = []
#     content_restricted = False
#     final_stable_age = -1
#     start_time = time.time()
#     logging.info(f"Performing face analysis for {duration_seconds} seconds...")
#
#     while time.time() - start_time < duration_seconds:
#         ret, frame = cap.read()
#         if not ret:
#             logging.warning("Cannot read frame from webcam.")
#             time.sleep(0.1)
#             continue
#
#         name, face_coords = predict_face(frame)
#         processed_face_in_frame = (face_coords is not None)
#         current_frame_restricted = False
#         stable_age = -1
#
#         if processed_face_in_frame and name not in ["No face", "Error", "Unknown"]:
#             predicted_age = predict_age(frame, face_coords)
#             if predicted_age != -1:
#                 age_predictions.append(predicted_age)
#                 if len(age_predictions) > 5:
#                     age_predictions.pop(0)
#                 if age_predictions:
#                     stable_age = int(np.mean(age_predictions))
#                     final_stable_age = stable_age
#                     logging.debug(f"Detected: {name}, Predicted Age: {predicted_age}, Stable Age: {stable_age}")
#
#                 if stable_age != -1 and stable_age < 18:
#                     logging.info(f"Child condition met: Name={name}, Stable Age={stable_age}")
#                     current_frame_restricted = True
#
#         if current_frame_restricted:
#              content_restricted = True # Latch restriction if detected once
#
#     cap.release()
#     logging.info("Webcam released.")
#     logging.info(f"Face analysis complete. Restricted: {content_restricted}, Final Stable Age: {final_stable_age}")
#     return content_restricted, final_stable_age
#
# if __name__ == '__main__':
#     restricted, age = check_user_age(duration_seconds=10)
#     print(f"\n--- Direct Run Result ---")
#     print(f"Restricted: {restricted}")
#     print(f"Detected Age: {age}")
#     print(f"-------------------------")
#     if restricted:
#         print("🔴 Content is Restricted")
#     else:
#         print("✅ No Content Restriction") 