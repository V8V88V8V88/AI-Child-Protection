import cv2
import os
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def train_model():
    
    dataset_path = os.path.join(DATA_DIR, "family_dataset")
    if not os.path.exists(dataset_path) or not os.listdir(dataset_path):
        print(f"Error: Dataset folder '{dataset_path}' is missing or empty.")
        print("Please run the dataset creation script first.")
        return

    
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"Created models directory: {MODELS_DIR}")

    print(f"🔹 Loading images from '{dataset_path}'...")
    X = []  
    y = []  
    label_map = {}  
    current_label = 0

    
    for person in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person)

        if os.path.isdir(person_path):
            print(f"   Processing images for {person}...")
            image_count = 0
            label_map[current_label] = person  

            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                try:
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is None:
                        print(f"Warning: Could not read image {img_name} in {person_path}. Skipping.")
                        continue
                    img = cv2.resize(img, (100, 100))  
                    X.append(img.flatten())  
                    y.append(current_label)
                    image_count += 1
                except Exception as e:
                    print(f"Warning: Error processing image {img_name} in {person_path}: {e}. Skipping.")

            if image_count == 0:
                print(f"Warning: No valid images found for {person}. Removing from training.")
                del label_map[current_label] 
                
            else:
                 current_label += 1 

    if not X or not y:
        print("Error: No valid training data found after processing dataset folder.")
        return

    print("🔹 Training KNN model...")
    X = np.array(X)
    y = np.array(y)

    
    
    knn = KNeighborsClassifier(n_neighbors=min(3, len(np.unique(y)))) 
    knn.fit(X, y)

    
    model_filename = os.path.join(MODELS_DIR, "face_recognition_model.pkl")
    label_map_filename = os.path.join(MODELS_DIR, "label_map.pkl")
    try:
        with open(model_filename, "wb") as f:
            pickle.dump(knn, f)
        with open(label_map_filename, "wb") as f:
            pickle.dump(label_map, f)
        print(f"✅ Training complete! Model saved as {model_filename}")
        print(f"✅ Label map saved as {label_map_filename}")
    except Exception as e:
        print(f"Error saving model files: {e}")

if __name__ == '__main__':
    train_model() 