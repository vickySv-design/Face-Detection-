# 🎂 Face Detection Birthday App 🎉

A professional AI-powered face recognition application that detects specific people and triggers birthday celebrations with animations, music, and visual effects.

## 🌟 Features

### Core Functionality
- **Real-time Face Detection**: Uses face_recognition library for accurate face detection
- **Custom Model Training**: Train models for specific people with your own images
- **Birthday Celebrations**: Automatic celebration when the birthday person is detected
- **Multi-Model Support**: Create and switch between multiple trained models
- **Live Training Progress**: Real-time accuracy and elapsed time tracking during training

### Birthday Celebration Effects
- 🎵 **Birthday Music**: Plays custom MP3 audio (supports Bluetooth speakers)
- 🎊 **Confetti Animation**: Colorful confetti falling from top
- 🎈 **Flying Balloons**: 8 balloons floating up from bottom
- 🎆 **Fireworks**: Colorful firework bursts
- ✨ **Sparkles**: Random sparkle effects across screen
- 🎂 **Cake Animation**: Giant spinning cake emoji
- 🎉 **Glowing Banner**: Large animated banner with person's name in glowing text
- 🎵 **Audio Indicator**: Visual indicator showing audio is playing

### Professional UI
- Modern gradient purple/pink theme with birthday elements
- Glass-morphism cards with shadows
- Smooth animations and transitions
- Responsive design
- Real-time detection status display

## 📋 Requirements

### Python Dependencies
```
fastapi
uvicorn
opencv-python
face-recognition
numpy
scikit-learn
joblib
python-multipart
tqdm
```

### System Requirements
- Python 3.8+
- Webcam/Camera
- Windows/Linux/macOS
- Modern web browser (Chrome, Firefox, Edge)

## 🚀 Installation

1. **Clone/Download the project**
```bash
cd "C:\Users\vicky\Desktop\New folder\face app\FaceDetectBirthdayApp"
```

2. **Install Python dependencies**
```bash
pip install -r backend/requirements.txt
```

3. **Verify directory structure**
```
FaceDetectBirthdayApp/
├── backend/
│   ├── app.py
│   ├── train_faces.py
│   ├── dataset/
│   ├── models/
│   └── static/
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── logo/
│   └── Birthday wish.mp3
├── logo/
│   ├── 1000004843.png
│   └── 1000004843-circle.png
└── start_app.py
```

## 🎯 Usage

### Starting the Application

**Option 1: Using Python script**
```bash
python start_app.py
```

**Option 2: Using batch file (Windows)**
```bash
start_app.bat
```

**Option 3: Manual start**
```bash
cd backend
python app.py
```

The app will automatically:
- Detect available port (8000, 8001, or 8002)
- Start the backend server
- Open browser at `http://localhost:8000`

### Training a Model

1. **Prepare Training Images**
   - Create a folder with person's name in `backend/dataset/`
   - Add 4-10 clear face photos (different angles, lighting)
   - Supported formats: JPG, JPEG, PNG, BMP

2. **Upload Images via Web Interface**
   - Enter person's name
   - Select multiple images
   - Click "Upload Images" or "Upload & Auto-Train"

3. **Train the Model**
   - Enter model name
   - Click "Train New Model"
   - Wait for training to complete (30-120 seconds)
   - View accuracy and training time

4. **Load the Model**
   - Select model from dropdown
   - Click "Load Model"
   - Model is now active for detection

### Using Face Detection

1. **Start Camera**
   - Click "Start Camera" button
   - Allow camera permissions
   - Camera feed will appear

2. **Detection**
   - Face detection runs automatically every 1.5 seconds
   - Shows detected person's name and confidence
   - Unknown faces show as "Unknown"

3. **Birthday Celebration**
   - When birthday person is detected 3 times consecutively
   - Celebration triggers automatically
   - Music plays, animations start
   - Cooldown: 30 seconds between celebrations

## 🎨 Customization

### Change Birthday Audio
Replace `frontend/Birthday wish.mp3` with your audio file (keep same name)

### Adjust Detection Settings
In `backend/app.py`:
```python
DETECTION_THRESHOLD = 0.60  # Confidence threshold (0-1)
REQUIRED_CONSECUTIVE = 3     # Consecutive detections needed
```

### Modify Celebration Duration
In `frontend/app.js`:
```javascript
lastCelebrationTime < 30000  // Cooldown in milliseconds
```

## 🔧 Technical Details

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Face Detection**: face_recognition (dlib-based)
- **Model**: SVM classifier for multiple people, Distance-based for single person
- **Training**: 80/20 train-test split with accuracy calculation
- **API Endpoints**:
  - `GET /` - Serve frontend
  - `GET /api/status` - Server status
  - `GET /api/models` - List models
  - `POST /api/models/load` - Load model
  - `POST /api/train` - Train new model
  - `GET /api/train/progress/{model_name}` - Training progress
  - `POST /api/upload` - Upload images
  - `POST /infer` - Face detection
  - `GET /api/dataset` - Dataset info

### Frontend (Vanilla JS)
- **Auto-port detection**: Tries ports 8000, 8001, 8002
- **Real-time updates**: 2-second polling for training progress
- **Animations**: CSS keyframes + JavaScript
- **Camera**: MediaDevices API with fallback support

### Face Recognition Model
- **Single Person**: Distance-based model (threshold: 0.8)
- **Multiple People**: SVM with RBF kernel
- **Encoding**: 128-dimensional face embeddings
- **Detection**: HOG-based face detection for speed

## 📊 Model Performance

- **Training Time**: 30-120 seconds (depends on dataset size)
- **Accuracy**: Typically 85-100% with good training data
- **Detection Speed**: ~1.5 seconds per frame
- **Confidence Threshold**: 60% minimum for recognition

## 🐛 Troubleshooting

### Port Already in Use
- App automatically tries ports 8000, 8001, 8002
- Manually specify port in `backend/app.py`

### Camera Not Working
- Check browser permissions
- Ensure no other app is using camera
- Try different browser

### Audio Not Playing
- Click anywhere on page first (browser autoplay policy)
- Check browser console for errors
- Verify audio file exists in `frontend/`

### Low Detection Accuracy
- Add more training images (8-10 recommended)
- Use clear, well-lit photos
- Include different angles and expressions
- Retrain the model

### Face Not Detected
- Ensure good lighting
- Face camera directly
- Move closer to camera
- Check if model is loaded

## 📝 Project Structure

```
backend/
├── app.py                 # FastAPI server
├── train_faces.py         # Model training logic
├── dataset/              # Training images
│   └── [PersonName]/     # Person folders
├── models/               # Trained models
│   ├── [name]_model.joblib
│   ├── [name]_encoder.joblib
│   └── [name]_metrics.json
└── static/               # Static files

frontend/
├── index.html            # Main UI
├── app.js               # Frontend logic
├── logo/                # Logo images
└── Birthday wish.mp3    # Birthday audio

logo/
├── 1000004843.png           # Square logo
└── 1000004843-circle.png    # Circular logo (favicon)
```

## 🎓 How It Works

1. **Training Phase**:
   - Load images from dataset folder
   - Detect faces using face_recognition
   - Extract 128-dimensional face embeddings
   - Train SVM classifier (or distance model for single person)
   - Save model, encoder, and metrics

2. **Detection Phase**:
   - Capture frame from webcam
   - Detect faces in frame
   - Extract face embeddings
   - Compare with trained model
   - Return label and confidence

3. **Celebration Trigger**:
   - Track consecutive detections
   - Require 3 consecutive matches
   - Check 30-second cooldown
   - Trigger animations and audio

## 🔐 Security Notes

- App runs locally (no data sent to external servers)
- Face data stored locally in `backend/models/`
- Camera access requires user permission
- No personal data collection

## 📄 License

This project is for educational and personal use.

## 👨‍💻 Developer

Created for birthday celebrations with AI-powered face recognition.

## 🙏 Acknowledgments

- **face_recognition** library by Adam Geitgey
- **FastAPI** framework
- **Bootstrap** for UI components

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: ✅ Fully Functional
