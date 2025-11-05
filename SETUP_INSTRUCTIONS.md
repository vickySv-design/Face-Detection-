# Face Detection Birthday App - Setup Instructions

## Quick Start

### Option 1: Automatic Startup (Recommended)
1. **Double-click** `start_app.bat` (Windows)
2. **Or run** `python start_app.py`
3. The app will automatically:
   - Start the backend server
   - Open your browser to http://localhost:8000
   - Display the frontend interface

### Option 2: Manual Startup
1. **Start Backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Open Frontend:**
   - Open your browser
   - Go to http://localhost:8000

## Features Connected

### ✅ Backend API Endpoints
- `/api/status` - Check server and model status
- `/api/models` - List available models
- `/api/models/load` - Load a specific model
- `/api/train` - Train new model
- `/api/upload` - Upload training images
- `/api/dataset` - View dataset information
- `/infer` - Real-time face recognition
- `/recognize` - Single image recognition

### ✅ Frontend Features
- **Model Management**: Load existing models or train new ones
- **Camera Integration**: Real-time video feed with face detection
- **Dataset Management**: Upload training images for different people
- **Birthday Celebration**: Automatic confetti and audio when birthday person detected
- **Status Monitoring**: Real-time connection and detection status

## How to Use

### 1. First Time Setup
1. Start the application using one of the methods above
2. The server will automatically load any existing models
3. If no models exist, you'll see "No model loaded"

### 2. Add Training Data
1. Go to "Dataset Management" section
2. Enter a person's name (e.g., "PersonA", "John", etc.)
3. Select multiple photos of that person
4. Click "Upload Images"
5. Repeat for other people you want to recognize

### 3. Train a Model
1. After uploading images, go to "Model Management"
2. Enter a name for your model (e.g., "birthday_model")
3. Click "Train New Model"
4. Wait for training to complete
5. The model will automatically load when ready

### 4. Start Face Detection
1. Click "Start Camera" 
2. Allow camera access when prompted
3. The app will detect faces in real-time
4. When the birthday person is detected, celebration effects will trigger

## Pre-computed Embedding Support

The app also supports pre-computed face embeddings:

1. **Automatic Loading**: If `models/personA_mean_embedding.npy` exists, it loads automatically
2. **Create from Dataset**: Use `/api/embedding/create` to generate from PersonA images
3. **Manual Creation**: Place your own 128-dimensional numpy array as `personA_mean_embedding.npy`

## Troubleshooting

### Backend Won't Start
- Check if Python and required packages are installed
- Run: `pip install -r backend/requirements.txt`
- Ensure port 8000 is not in use

### Frontend Can't Connect
- Verify backend is running on http://localhost:8000
- Check browser console for errors
- Try refreshing the page

### Camera Not Working
- Allow camera permissions in browser
- Try a different browser (Chrome recommended)
- Check if camera is being used by another application

### No Face Detection
- Ensure a model is loaded (check status badge)
- Verify good lighting conditions
- Make sure face is clearly visible and not at extreme angles

## Testing Connection

Run the test script to verify everything is working:
```bash
python test_connection.py
```

This will check:
- Backend server status
- API endpoint availability  
- Model loading capability

## File Structure

```
FaceDetectBirthdayApp/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── models/                # Trained models and embeddings
│   ├── dataset/               # Training images
│   └── requirements.txt       # Python dependencies
├── frontend/
│   └── index.html            # Complete web interface
├── start_app.py              # Automatic startup script
├── start_app.bat             # Windows batch file
└── test_connection.py        # Connection test script
```

## Success Indicators

When everything is working correctly, you should see:
- ✅ "Backend server started successfully!"
- ✅ Browser opens to http://localhost:8000
- ✅ Model status shows "Ready" or "Loaded"
- ✅ Camera feed appears when "Start Camera" is clicked
- ✅ Face detection results appear in real-time

The frontend and backend are now fully connected and ready to use!