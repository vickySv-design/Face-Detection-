import os
import cv2
import numpy as np
import face_recognition
import joblib
from sklearn import svm
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from tqdm import tqdm
import time
import json

class DistanceModel:
    """Distance-based model for single person recognition"""
    def __init__(self, reference_embedding):
        self.reference_embedding = reference_embedding
    
    def predict_proba(self, face_encodings):
        results = []
        for encoding in face_encodings:
            distance = np.linalg.norm(encoding - self.reference_embedding)
            # Map distance to confidence: distance 0.0-0.8 -> confidence 1.0-0.5
            confidence = max(0.0, 1.0 - (distance / 0.8))
            results.append([1 - confidence, confidence])
        return np.array(results)

def load_dataset(dataset_path):
    """
    Load images and labels from the dataset directory.
    Each subdirectory in dataset_path should be named after the person and contain their images.
    """
    encodings = []
    labels = []
    
    # Create necessary directories if they don't exist
    os.makedirs('embeddings', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Get list of people (subdirectories in dataset_path)
    people = [d for d in os.listdir(dataset_path) 
              if os.path.isdir(os.path.join(dataset_path, d))]
    
    if not people:
        raise ValueError("No person directories found in the dataset folder.")
    
    print(f"Found {len(people)} people in the dataset.")
    
    for person in tqdm(people, desc="Processing people"):
        person_dir = os.path.join(dataset_path, person)
        
        # Get list of images for the current person
        image_files = [f for f in os.listdir(person_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        if not image_files:
            print(f"Warning: No images found for {person}")
            continue
            
        for image_file in tqdm(image_files, desc=f"Processing {person}", leave=False):
            image_path = os.path.join(person_dir, image_file)
            
            try:
                # Load image directly with face_recognition (more reliable)
                image = face_recognition.load_image_file(image_path)
                
                # Resize large images for faster processing
                max_size = 800
                height, width = image.shape[:2]
                if max(height, width) > max_size:
                    scale = max_size / max(height, width)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    image = cv2.resize(image, (new_width, new_height))
                
                # Try CNN model first for better detection
                face_locations = face_recognition.face_locations(image, model='cnn')
                
                # If no faces found, try HOG with more upsampling
                if not face_locations:
                    face_locations = face_recognition.face_locations(image, model='hog', number_of_times_to_upsample=2)
                
                # If still no faces found, skip this image
                if not face_locations:
                    print(f"Warning: No face found in {image_path}")
                    continue
                
                # Use the largest face if multiple detected
                if len(face_locations) > 1:
                    face_locations = [max(face_locations, key=lambda loc: (loc[2]-loc[0])*(loc[1]-loc[3]))]
                    
                # Encode the face
                face_encodings = face_recognition.face_encodings(image, face_locations, num_jitters=1)
                
                if face_encodings:  # If encoding was successful
                    encodings.append(face_encodings[0])
                    labels.append(person)
                    
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
                continue
    
    if not encodings:
        raise ValueError("No valid face encodings were generated from the dataset.")
        
    return np.array(encodings), np.array(labels)

def train_face_recognition_model(model_name='default', progress_callback=None):
    """
    Train a face recognition model with the given name.
    Returns (success, message, accuracy) tuple.
    """
    start_time = time.time()
    
    try:
        # Set up paths
        dataset_path = 'dataset'
        model_path = os.path.join('models', f'{model_name}_model.joblib')
        encoder_path = os.path.join('models', f'{model_name}_encoder.joblib')
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        print(f"\n[TRAINING] Starting model: {model_name}")
        if progress_callback:
            progress_callback(10, "Loading dataset...", time.time() - start_time)
        
        # Load and prepare dataset
        print("[TRAINING] Loading dataset...")
        X, y = load_dataset(dataset_path)
        
        if len(X) == 0 or len(y) == 0:
            return False, "No valid training data found. Please add more images to the dataset.", 0.0
        
        print(f"[TRAINING] Dataset loaded: {len(X)} samples from {len(set(y))} classes")
        if progress_callback:
            progress_callback(30, f"Dataset loaded: {len(X)} samples from {len(set(y))} classes", time.time() - start_time)
        
        # For single person, use distance-based approach
        if len(set(y)) == 1:
            print("[TRAINING] Single person detected - using distance-based model")
            if progress_callback:
                progress_callback(50, "Creating distance-based model...", time.time() - start_time)
            
            # Calculate mean embedding
            mean_embedding = np.mean(X, axis=0)
            clf = DistanceModel(mean_embedding)
            
            # Create encoder with person name and Unknown
            le = LabelEncoder()
            le.classes_ = np.array(['Unknown', y[0]])
            
            accuracy = 1.0
            print(f"[TRAINING] Distance model created for: {y[0]}")
        else:
            # Encode the labels
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            
            print("[TRAINING] Encoding labels and splitting dataset...")
            if progress_callback:
                progress_callback(40, "Splitting dataset for validation...", time.time() - start_time)
            
            # Split data for training and validation
            test_size = 0.2 if len(X) >= 10 else 0.1
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
            )
            
            print("[TRAINING] Training SVM classifier...")
            if progress_callback:
                progress_callback(50, "Training SVM classifier...", time.time() - start_time)
            
            # Create and train the SVM classifier
            clf = svm.SVC(
                kernel='rbf',
                probability=True,
                gamma='scale',
                C=1.0
            )
            clf.fit(X_train, y_train)
            
            print("[TRAINING] Evaluating model accuracy...")
            if progress_callback:
                progress_callback(80, "Evaluating model accuracy...", time.time() - start_time)
            
            # Calculate accuracy
            y_pred = clf.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
        print(f"[TRAINING] Model accuracy: {accuracy:.2%}")
        
        if progress_callback:
            progress_callback(90, f"Model accuracy: {accuracy:.2%}", time.time() - start_time)
        
        # Save the model and label encoder
        print("[TRAINING] Saving model...")
        joblib.dump(clf, model_path)
        joblib.dump(le, encoder_path)
        
        # Save training metrics
        metrics = {
            'accuracy': float(accuracy),
            'training_samples': len(X),
            'test_samples': len(X) if len(set(y)) == 1 else len(X_test),
            'classes': len(set(y)),
            'training_time': time.time() - start_time
        }
        
        metrics_path = os.path.join('models', f'{model_name}_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"[TRAINING] ✓ Completed! Accuracy: {accuracy:.2%}, Time: {time.time() - start_time:.1f}s\n")
        if progress_callback:
            progress_callback(100, "Training completed successfully!", time.time() - start_time)
        
        return True, f"Model '{model_name}' trained successfully with {accuracy:.2%} accuracy ({len(X)} samples from {len(set(y))} classes)", accuracy
        
    except Exception as e:
        return False, f"Error training model: {str(e)}", 0.0

def main():
    import argparse
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Train a face recognition model')
    parser.add_argument('--model-name', type=str, default='default',
                       help='Name for the trained model (default: default)')
    args = parser.parse_args()
    
    print(f"Training model: {args.model_name}")
    success, message, accuracy = train_face_recognition_model(args.model_name)
    
    if success:
        print(f"\n✅ {message}")
        print(f"Model saved to: models/{args.model_name}_model.joblib")
        print(f"Label encoder saved to: models/{args.model_name}_encoder.joblib")
        print(f"Training accuracy: {accuracy:.2%}")
    else:
        print(f"\n❌ {message}")

if __name__ == "__main__":
    main()
