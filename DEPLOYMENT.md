# 🚀 Deployment Guide

## GitHub Deployment

### 1. Push to GitHub

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Face Detection Birthday App"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/face-detection-birthday-app.git

# Push to GitHub
git push -u origin main
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/face-detection-birthday-app.git
cd face-detection-birthday-app

# Install dependencies
pip install -r requirements.txt

# Run application
python start_app.py
```

## Local Deployment

### Quick Start

1. **Install Python 3.8+**
   - Download from https://www.python.org/downloads/

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   python start_app.py
   ```
   Or double-click `start_app.bat` (Windows)

4. **Access Application**
   - Browser opens automatically at `http://localhost:8000`
   - Or manually open: `http://localhost:8000`

## Docker Deployment (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "start_app.py"]
```

### Build and Run

```bash
# Build image
docker build -t birthday-app .

# Run container
docker run -p 8000:8000 birthday-app
```

## Cloud Deployment

### Heroku

1. Create `Procfile`:
   ```
   web: cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### AWS EC2

1. Launch EC2 instance (Ubuntu)
2. SSH into instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```
4. Run application:
   ```bash
   python3 start_app.py
   ```

### DigitalOcean

1. Create Droplet (Ubuntu)
2. Follow AWS EC2 steps above

## Network Deployment

### Access from Other Devices (Same Network)

1. Find your IP address:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig`

2. Update `backend/app.py`:
   ```python
   uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
   ```

3. Access from other devices:
   ```
   http://YOUR_IP_ADDRESS:8000
   ```

## Production Considerations

### Security
- Use HTTPS in production
- Add authentication if needed
- Restrict CORS origins
- Use environment variables for sensitive data

### Performance
- Use production ASGI server (Gunicorn + Uvicorn)
- Enable caching
- Optimize model loading
- Use CDN for static files

### Monitoring
- Add logging
- Monitor server health
- Track model performance
- Set up alerts

## Troubleshooting

### Port Issues
- Change port in `start_app.py` if 8000 is occupied
- Check firewall settings

### Camera Access
- HTTPS required for camera on remote devices
- Check browser permissions

### Dependencies
- Use virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  ```

## Environment Variables

Create `.env` file:
```
PORT=8000
HOST=0.0.0.0
DEBUG=False
```

## Backup

Backup important directories:
- `backend/models/` - Trained models
- `backend/dataset/` - Training images
- `frontend/Birthday wish.mp3` - Audio file

---

**Ready for deployment!** 🚀
