import os
import cv2
import numpy as np
import face_recognition
import joblib
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any, List
import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
from contextlib import asynccontextmanager
import json
import time

# Create necessary directories
os.makedirs('models', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('dataset', exist_ok=True)

# Get the absolute path to the frontend directory
FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Global variables to store the model and encoder
model = None
encoder = None
current_model_name = None

# Detection tracking
DETECTION_THRESHOLD = 0.60
CONSECUTIVE_DETECTIONS = {}
REQUIRED_CONSECUTIVE = 3
BIRTHDAY_PERSON = None
LAST_DETECTION_TIME = {}

class DetectionResult(BaseModel):
    label: str
    confidence: float
    is_birthday_person: bool
    message: str = ""

def load_models(model_name='default'):
    """Load the trained model and label encoder"""
    global model, encoder, BIRTHDAY_PERSON, current_model_name
    
    model_path = os.path.join('models', f'{model_name}_model.joblib')
    encoder_path = os.path.join('models', f'{model_name}_encoder.joblib')
    
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        raise FileNotFoundError(f"Model '{model_name}' not found. Please train the model first.")
    
    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    current_model_name = model_name
    
    # Set the birthday person (find first non-Unknown class)
    BIRTHDAY_PERSON = None
    for cls in encoder.classes_:
        if cls != 'Unknown':
            BIRTHDAY_PERSON = cls
            break
    
    if not BIRTHDAY_PERSON and encoder.classes_.size > 0:
        BIRTHDAY_PERSON = encoder.classes_[0]
    
    print(f"Loaded model '{model_name}'. Birthday person set to: {BIRTHDAY_PERSON}")
    
    return {"success": True, "message": f"Model '{model_name}' loaded successfully", "birthday_person": BIRTHDAY_PERSON}

def load_precomputed_embedding():
    """Load pre-computed face embedding if available"""
    global model, encoder, BIRTHDAY_PERSON, current_model_name
    
    embedding_path = os.path.join('models', 'personA_mean_embedding.npy')
    
    if os.path.exists(embedding_path):
        try:
            # Load the pre-computed embedding
            embedding = np.load(embedding_path)
            
            # Create a simple model that uses the embedding for comparison
            class SimpleEmbeddingModel:
                def __init__(self, reference_embedding):
                    self.reference_embedding = reference_embedding
                
                def predict_proba(self, face_encodings):
                    # Calculate similarity with reference embedding
                    similarities = []
                    for encoding in face_encodings:
                        # Use face_recognition's compare_faces for similarity
                        distance = np.linalg.norm(encoding - self.reference_embedding)
                        # Convert distance to probability (closer = higher probability)
                        probability = max(0, 1 - distance)
                        similarities.append([1 - probability, probability])  # [unknown, personA]
                    return np.array(similarities)
            
            # Create a simple encoder
            class SimpleEncoder:
                def __init__(self):
                    self.classes_ = np.array(['Unknown', 'PersonA'])
                
                def inverse_transform(self, indices):
                    return self.classes_[indices]
            
            model = SimpleEmbeddingModel(embedding)
            encoder = SimpleEncoder()
            current_model_name = 'precomputed_embedding'
            BIRTHDAY_PERSON = 'PersonA'
            
            print(f"Loaded pre-computed embedding. Birthday person set to: {BIRTHDAY_PERSON}")
            return {"success": True, "message": "Pre-computed embedding loaded successfully"}
            
        except Exception as e:
            print(f"Failed to load pre-computed embedding: {str(e)}")
            return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "No pre-computed embedding found"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup code
    print("\n" + "="*60)
    print("🎂 FACE DETECTION BIRTHDAY APP - STARTING UP")
    print("="*60)
    
    print("\n[STARTUP] Creating directories...")
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('dataset', exist_ok=True)
    print("[STARTUP] ✓ Directories ready")
    
    print("\n[STARTUP] Checking for existing models...")
    # Try to load pre-computed embedding first
    embedding_result = load_precomputed_embedding()
    if embedding_result["success"]:
        print("[STARTUP] ✓ Pre-computed embedding loaded")
    else:
        # Try to load default model if available
        try:
            load_models('default')
            print("[STARTUP] ✓ Default model loaded")
        except FileNotFoundError:
            print("[STARTUP] ⚠ No models found")
            print("[STARTUP] → Upload images and train a model to get started")
    
    print("\n" + "="*60)
    print("✓ APPLICATION READY - Listening for requests...")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown code
    print("\n" + "="*60)
    print("🛑 APPLICATION SHUTTING DOWN")
    print("="*60 + "\n")

# Initialize FastAPI app with lifespan handler
app = FastAPI(title="Face Detection Birthday App", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory=FRONTEND_PATH), name="frontend")
app.mount("/logo", StaticFiles(directory=os.path.join(FRONTEND_PATH, 'logo')), name="logo")

@app.get("/Birthday wish.mp3")
async def serve_audio():
    """Serve the birthday audio file"""
    return FileResponse(os.path.join(FRONTEND_PATH, 'Birthday wish.mp3'))

@app.get("/app.js")
async def serve_app_js():
    """Serve the app.js file"""
    return FileResponse(os.path.join(FRONTEND_PATH, 'app.js'))

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse(os.path.join(FRONTEND_PATH, 'index.html'))

@app.get("/api/status")
async def get_status():
    """Get the current status of the application"""
    print("[STATUS] Status check requested")
    if model is None or encoder is None:
        print("[STATUS] → No model loaded")
        return {
            "status": "no_model_loaded",
            "message": "No model loaded. Please load or train a model first."
        }
    print(f"[STATUS] → Ready | Model: {current_model_name} | Birthday Person: {BIRTHDAY_PERSON}")
    return {
        "status": "ready",
        "current_model": current_model_name,
        "birthday_person": BIRTHDAY_PERSON,
        "message": f"Model '{current_model_name}' is loaded and ready"
    }

@app.get("/api/models")
async def list_models():
    """List all available models with their metrics"""
    try:
        print("[MODELS] Listing available models...")
        if not os.path.exists('models'):
            print("[MODELS] → No models directory found")
            return {"success": True, "models": [], "message": "No models found"}
            
        # Get all model files and extract unique model names
        model_files = [f for f in os.listdir('models') if f.endswith('_model.joblib')]
        models_data = []
        
        for model_file in model_files:
            model_name = model_file.replace('_model.joblib', '')
            model_info = {"name": model_name, "accuracy": None, "training_time": None}
            
            # Try to load metrics if available
            metrics_path = os.path.join('models', f'{model_name}_metrics.json')
            if os.path.exists(metrics_path):
                try:
                    with open(metrics_path, 'r') as f:
                        metrics = json.load(f)
                        model_info["accuracy"] = metrics.get('accuracy', None)
                        model_info["training_time"] = metrics.get('training_time', None)
                        model_info["training_samples"] = metrics.get('training_samples', None)
                        model_info["classes"] = metrics.get('classes', None)
                except:
                    pass
            
            models_data.append(model_info)
        
        print(f"[MODELS] → Found {len(models_data)} models")
        return {
            "success": True,
            "models": [m["name"] for m in models_data],
            "models_data": models_data,
            "current_model": current_model_name,
            "message": f"Found {len(models_data)} models"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/models/load")
async def load_model_endpoint(model_name: str):
    """Load a specific model"""
    try:
        print(f"\n[MODEL] Loading model: {model_name}")
        result = load_models(model_name)
        if result.get('success'):
            print(f"[MODEL] ✓ Model '{model_name}' loaded successfully\n")
        else:
            print(f"[MODEL] ✗ Failed to load model '{model_name}'\n")
        return result
    except Exception as e:
        print(f"[MODEL] ✗ Error: {str(e)}\n")
        return {"success": False, "error": str(e)}

@app.post("/api/embedding/create")
async def create_precomputed_embedding():
    """Create a pre-computed embedding from PersonA images in dataset"""
    try:
        person_dir = os.path.join('dataset', 'PersonA')
        if not os.path.exists(person_dir) or not os.listdir(person_dir):
            return {"success": False, "error": "No PersonA images found in dataset/PersonA directory"}
        
        # Collect all face encodings from PersonA images
        encodings = []
        processed_files = []
        
        for filename in os.listdir(person_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_path = os.path.join(person_dir, filename)
                try:
                    # Load and process image
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if face_encodings:
                        encodings.append(face_encodings[0])
                        processed_files.append(filename)
                    else:
                        print(f"No face found in {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        if not encodings:
            return {"success": False, "error": "No valid face encodings found in PersonA images"}
        
        # Calculate mean embedding
        mean_embedding = np.mean(encodings, axis=0)
        
        # Save the embedding
        embedding_path = os.path.join('models', 'personA_mean_embedding.npy')
        np.save(embedding_path, mean_embedding)
        
        # Load the new embedding
        result = load_precomputed_embedding()
        
        return {
            "success": True,
            "message": f"Pre-computed embedding created from {len(encodings)} images",
            "processed_files": processed_files,
            "embedding_shape": mean_embedding.shape
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Global variable to store training progress
training_progress = {}

@app.post("/api/train")
async def train_model_endpoint(model_name: str):
    """Train a new model with the given name"""
    try:
        print("\n" + "="*60)
        print(f"[TRAIN] Training request received for: {model_name}")
        print("="*60)
        
        # Check if dataset directory exists and has subdirectories
        if not os.path.exists('dataset') or not os.listdir('dataset'):
            print("[TRAIN] ✗ No dataset found\n")
            return {"success": False, "error": "No dataset found. Please add training images to the 'dataset' directory."}
        
        # Initialize progress tracking
        training_progress[model_name] = {
            "progress": 0,
            "message": "Initializing...",
            "elapsed_time": 0,
            "accuracy": 0.0
        }
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Progress callback function
        def progress_callback(progress, message, elapsed_time):
            training_progress[model_name] = {
                "progress": progress,
                "message": message,
                "elapsed_time": elapsed_time
            }
        
        # Train the model
        from train_faces import train_face_recognition_model
        success, message, accuracy = train_face_recognition_model(model_name, progress_callback)
        
        if success:
            # Update final progress
            training_progress[model_name]["accuracy"] = accuracy
            
            # Load the newly trained model
            try:
                print(f"[TRAIN] Loading trained model...")
                load_models(model_name)
                print("="*60 + "\n")
                return {
                    "success": True, 
                    "message": message,
                    "model_name": model_name,
                    "accuracy": accuracy
                }
            except Exception as e:
                print(f"[TRAIN] ✗ Failed to load: {str(e)}")
                print("="*60 + "\n")
                return {
                    "success": False, 
                    "error": f"Model trained but failed to load: {str(e)}",
                    "model_name": model_name,
                    "accuracy": accuracy
                }
        else:
            print(f"[TRAIN] ✗ Training failed: {message}")
            print("="*60 + "\n")
            return {
                "success": False, 
                "error": message,
                "model_name": model_name,
                "accuracy": 0.0
            }
            
    except Exception as e:
        error_msg = f"Error during model training: {str(e)}"
        print(error_msg)
        return {
            "success": False, 
            "error": error_msg,
            "model_name": model_name,
            "accuracy": 0.0
        }

@app.get("/api/train/progress/{model_name}")
async def get_training_progress(model_name: str):
    """Get real-time training progress for a model"""
    if model_name in training_progress:
        return {
            "success": True,
            **training_progress[model_name]
        }
    else:
        return {
            "success": False,
            "error": "No training in progress for this model"
        }

@app.get("/api/dataset")
async def get_dataset():
    """Get list of people in the dataset"""
    try:
        print("[DATASET] Checking dataset...")
        if not os.path.exists('dataset') or not os.listdir('dataset'):
            print("[DATASET] → Empty dataset")
            return {"success": False, "error": "Dataset directory is empty"}
            
        people = [d for d in os.listdir('dataset') 
                 if os.path.isdir(os.path.join('dataset', d))]
        
        print(f"[DATASET] → Found {len(people)} people: {', '.join(people)}")
        return {
            "success": True,
            "people": people,
            "count": len(people)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/upload")
async def upload_files(
    person_name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Upload training images for a person"""
    try:
        print(f"\n[UPLOAD] Receiving {len(files)} images for {person_name}")
        # Create person directory if it doesn't exist
        person_dir = os.path.join('dataset', person_name)
        os.makedirs(person_dir, exist_ok=True)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if file.filename:
                file_path = os.path.join(person_dir, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                saved_files.append(file.filename)
                print(f"[UPLOAD] Saved: {file.filename}")
        
        print(f"[UPLOAD] ✓ Completed: {len(saved_files)} files for {person_name}\n")
        return {
            "success": True,
            "message": f"Uploaded {len(saved_files)} files for {person_name}",
            "saved_files": saved_files
        }
    except Exception as e:
        print(f"[UPLOAD] ✗ Error: {str(e)}\n")
        return {"success": False, "error": str(e)}

@app.post("/recognize")
async def recognize_face(file: UploadFile = File(...)):
    """Recognize a face from an uploaded image"""
    if model is None or encoder is None:
        return {"success": False, "error": "No model loaded. Please load or train a model first."}
    
    try:
        # Read the uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image")
        
        # Convert to RGB (face_recognition uses RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find all face locations in the image
        face_locations = face_recognition.face_locations(rgb_img)
        
        if not face_locations:
            return {"success": True, "label": "No face detected", "confidence": 0.0, "is_birthday_person": False}
        
        # Encode the first face found
        face_encodings = face_recognition.face_encodings(rgb_img, [face_locations[0]])
        
        if not face_encodings:
            return {"success": True, "label": "Could not encode face", "confidence": 0.0, "is_birthday_person": False}
        
        # Predict the label and confidence
        face_encoding = face_encodings[0]
        predictions = model.predict_proba([face_encoding])[0]
        
        # Get the best prediction
        best_class_idx = np.argmax(predictions)
        confidence = predictions[best_class_idx]
        
        # Only consider predictions above threshold
        if confidence < DETECTION_THRESHOLD:
            return {
                "success": True, 
                "label": "Unknown", 
                "confidence": float(confidence), 
                "is_birthday_person": False
            }
        
        # Get the label name
        label = encoder.inverse_transform([best_class_idx])[0]
        
        # Check if this is the birthday person
        is_birthday_person = (label == BIRTHDAY_PERSON)
        
        return {
            "success": True,
            "label": label,
            "confidence": float(confidence),
            "is_birthday_person": is_birthday_person,
            "model_used": current_model_name
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/infer")
async def infer_face(file: UploadFile = File(...)):
    """Endpoint for face recognition from the frontend"""
    global CONSECUTIVE_DETECTIONS, LAST_DETECTION_TIME
    
    if model is None or encoder is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    try:
        # Read the uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not read image")
        
        # Resize for faster processing
        max_size = 640
        height, width = img.shape[:2]
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            img = cv2.resize(img, (int(width * scale), int(height * scale)))
        
        # Convert to RGB (face_recognition uses RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find all face locations in the image (optimized)
        face_locations = face_recognition.face_locations(rgb_img, model='hog', number_of_times_to_upsample=1)
        
        if not face_locations:
            CONSECUTIVE_DETECTIONS['birthday_person'] = 0
            return {"label": "No face detected", "confidence": 0, "is_birthday_person": False}
        
        # Use the largest face if multiple detected
        if len(face_locations) > 1:
            face_locations = [max(face_locations, key=lambda loc: (loc[2]-loc[0])*(loc[1]-loc[3]))]
        
        # Encode the face
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations, num_jitters=1)
        
        if not face_encodings:
            CONSECUTIVE_DETECTIONS['birthday_person'] = 0
            return {"label": "Could not encode face", "confidence": 0, "is_birthday_person": False}
        
        # Predict the label and confidence
        face_encoding = face_encodings[0]
        predictions = model.predict_proba([face_encoding])[0]
        
        # Get the best prediction
        best_class_idx = np.argmax(predictions)
        confidence = predictions[best_class_idx]
        
        # Get the label name
        label = encoder.inverse_transform([best_class_idx])[0]
        
        # Debug: print all predictions
        print(f"[DETECT] Predictions: {dict(zip(encoder.classes_, predictions))}")
        
        # Only consider predictions above threshold (unless it's already labeled as Unknown)
        if confidence < DETECTION_THRESHOLD and label != 'Unknown':
            label = 'Unknown'
            CONSECUTIVE_DETECTIONS['birthday_person'] = 0
            print(f"[DETECT] Unknown | Confidence: {confidence:.2%} (below threshold)")
            return {"label": "Unknown", "confidence": float(confidence), "is_birthday_person": False}
        
        # If model predicted Unknown, use that
        if label == 'Unknown':
            CONSECUTIVE_DETECTIONS['birthday_person'] = 0
            print(f"[DETECT] Unknown | Confidence: {confidence:.2%}")
            return {"label": "Unknown", "confidence": float(confidence), "is_birthday_person": False}
        
        # Check if this is the birthday person
        is_birthday_person = (label == BIRTHDAY_PERSON)
        
        # Track consecutive detections for the birthday person
        current_time = time.time()
        if is_birthday_person:
            last_time = LAST_DETECTION_TIME.get('birthday_person', 0)
            # Reset counter if too much time has passed (>3 seconds)
            if current_time - last_time > 3:
                CONSECUTIVE_DETECTIONS['birthday_person'] = 1
            else:
                CONSECUTIVE_DETECTIONS['birthday_person'] = CONSECUTIVE_DETECTIONS.get('birthday_person', 0) + 1
            LAST_DETECTION_TIME['birthday_person'] = current_time
        else:
            CONSECUTIVE_DETECTIONS['birthday_person'] = 0
        
        # Only confirm if we have enough consecutive detections
        is_confirmed_birthday = (CONSECUTIVE_DETECTIONS.get('birthday_person', 0) >= REQUIRED_CONSECUTIVE)
        
        # Print detection result
        if is_confirmed_birthday:
            print(f"[DETECT] ✓ {label} detected! Confidence: {confidence:.2%} [BIRTHDAY PERSON]")
        else:
            print(f"[DETECT] {label} | Confidence: {confidence:.2%}")
        
        return {
            "label": label,
            "confidence": float(confidence),
            "is_birthday_person": is_confirmed_birthday
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    # Run the FastAPI app on port 8001 if 8000 is blocked
    import socket
    port = 8000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', port))
        sock.close()
    except:
        port = 8001
        print(f"Port 8000 is in use, using port {port} instead")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)