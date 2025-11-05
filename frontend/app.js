// Auto-detect API port
let API_BASE = 'http://localhost:8000';

// Try to detect the correct port
async function detectPort() {
    const ports = [8000, 8001, 8002];
    for (const port of ports) {
        try {
            const response = await fetch(`http://localhost:${port}/api/status`, { 
                method: 'GET',
                signal: AbortSignal.timeout(1000)
            });
            if (response.ok) {
                API_BASE = `http://localhost:${port}`;
                console.log(`Connected to server on port ${port}`);
                return true;
            }
        } catch (e) {
            // Port not available, try next
        }
    }
    return false;
}

// DOM Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const cameraToggle = document.getElementById('cameraToggle');
const modelSelect = document.getElementById('modelSelect');
const modelInfo = document.getElementById('modelInfo');
const loadModelBtn = document.getElementById('loadModelBtn');
const trainModelBtn = document.getElementById('trainModelBtn');
const newModelName = document.getElementById('newModelName');
const uploadBtn = document.getElementById('uploadBtn');
const uploadAndTrainBtn = document.getElementById('uploadAndTrainBtn');
const personName = document.getElementById('personName');
const imageUpload = document.getElementById('imageUpload');
const uploadStatus = document.getElementById('uploadStatus');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const trainProgressContainer = document.getElementById('trainProgressContainer');
const trainProgressBar = document.getElementById('trainProgressBar');
const trainProgressText = document.getElementById('trainProgressText');
const trainStats = document.getElementById('trainStats');
const elapsedTime = document.getElementById('elapsedTime');
const currentAccuracy = document.getElementById('currentAccuracy');
const progressPercent = document.getElementById('progressPercent');
const uploadTrainStats = document.getElementById('uploadTrainStats');
const uploadElapsedTime = document.getElementById('uploadElapsedTime');
const uploadAccuracy = document.getElementById('uploadAccuracy');
const refreshDatasetBtn = document.getElementById('refreshDatasetBtn');
const datasetInfo = document.getElementById('datasetInfo');
const detectionStatus = document.getElementById('detectionStatus');
const birthdayAudio = document.getElementById('birthdayAudio');
const statusMessage = document.getElementById('statusMessage');
const modelStatus = document.getElementById('modelStatus');

let stream = null;
let isDetecting = false;
let detectionInterval = null;
let currentModel = null;
let trainingProgressInterval = null;
let isProcessing = false;
let isAudioPlaying = false;
let lastCelebrationTime = 0;

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    
    // Detect the correct port first
    const connected = await detectPort();
    if (!connected) {
        showStatus('Cannot connect to server on any port. Please start the backend server.', 'danger');
        modelStatus.textContent = 'Server offline';
        modelStatus.className = 'badge bg-danger';
        return;
    }
    
    // Now load everything
    checkServerStatus();
    loadModels();
    loadDatasetInfo();
});

function setupEventListeners() {
    cameraToggle.addEventListener('click', toggleCamera);
    modelSelect.addEventListener('change', () => {
        loadModelBtn.disabled = !modelSelect.value;
        updateModelInfo();
    });
    loadModelBtn.addEventListener('click', loadSelectedModel);
    trainModelBtn.addEventListener('click', trainNewModel);
    uploadBtn.addEventListener('click', uploadImages);
    uploadAndTrainBtn.addEventListener('click', uploadAndAutoTrain);
    refreshDatasetBtn.addEventListener('click', loadDatasetInfo);
    personName.addEventListener('input', updateUploadButtonState);
    imageUpload.addEventListener('change', updateUploadButtonState);
    newModelName.addEventListener('input', () => {
        trainModelBtn.disabled = !newModelName.value.trim();
    });
}

function updateUploadButtonState() {
    const hasData = personName.value.trim() && imageUpload.files.length > 0;
    uploadBtn.disabled = !hasData;
    uploadAndTrainBtn.disabled = !hasData;
}

function showProgress(container, bar, text, percentage, message) {
    container.style.display = 'block';
    bar.style.width = percentage + '%';
    text.textContent = message;
}

function hideProgress(container) {
    container.style.display = 'none';
}

function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `alert alert-${type}`;
    statusMessage.style.display = 'block';
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

function formatTime(seconds) {
    if (seconds < 60) {
        return `${Math.round(seconds)}s`;
    } else {
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        return `${mins}m ${secs}s`;
    }
}

function updateModelInfo() {
    const selectedModel = modelSelect.value;
    if (!selectedModel) {
        modelInfo.textContent = '';
        return;
    }
    
    const modelData = window.modelsData?.find(m => m.name === selectedModel);
    if (modelData && modelData.accuracy !== null) {
        const accuracy = (modelData.accuracy * 100).toFixed(1);
        const time = modelData.training_time ? formatTime(modelData.training_time) : 'Unknown';
        modelInfo.innerHTML = `📊 Accuracy: ${accuracy}% | ⏱️ Training Time: ${time}`;
    } else {
        modelInfo.textContent = 'No training metrics available';
    }
}

async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        
        if (data.status === 'ready') {
            modelStatus.textContent = `Ready: ${data.current_model}`;
            modelStatus.className = 'badge bg-success';
            currentModel = data.current_model;
        } else {
            modelStatus.textContent = 'No model loaded';
            modelStatus.className = 'badge bg-warning';
        }
    } catch (error) {
        console.error('Error checking server status:', error);
        modelStatus.textContent = 'Server offline';
        modelStatus.className = 'badge bg-danger';
        showStatus('Cannot connect to server. Make sure backend is running.', 'danger');
    }
}

async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/api/models`);
        const data = await response.json();
        
        if (data.success) {
            modelSelect.innerHTML = '<option value="">Select a model...</option>';
            window.modelsData = data.models_data || [];
            
            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    if (model === data.current_model) {
                        option.selected = true;
                        currentModel = model;
                    }
                    modelSelect.appendChild(option);
                });
                showStatus(`Found ${data.models.length} models`, 'info');
            } else {
                showStatus('No models found. Train a model first.', 'warning');
            }
            
            loadModelBtn.disabled = !modelSelect.value;
            updateModelInfo();
        } else {
            showStatus('Failed to load models: ' + (data.error || 'Unknown error'), 'danger');
        }
    } catch (error) {
        console.error('Error loading models:', error);
        showStatus('Error connecting to server: ' + error.message, 'danger');
    }
}

async function loadDatasetInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/dataset`);
        const data = await response.json();
        
        if (data.success) {
            if (data.count === 0) {
                datasetInfo.innerHTML = '<div class="text-muted">No people in dataset. Upload images to get started.</div>';
                return;
            }
            
            let html = `<div><strong>${data.count} people in dataset:</strong></div><ul class="list-unstyled mt-2">`;
            
            data.people.forEach(person => {
                html += `<li>👤 ${person}</li>`;
            });
            
            html += '</ul>';
            datasetInfo.innerHTML = html;
        } else {
            datasetInfo.innerHTML = `<div class="text-danger">Error: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Error loading dataset info:', error);
        datasetInfo.innerHTML = `<div class="text-danger">Error loading dataset: ${error.message}</div>`;
    }
}

async function loadSelectedModel() {
    const modelName = modelSelect.value;
    if (!modelName) return;
    
    loadModelBtn.disabled = true;
    loadModelBtn.innerHTML = 'Loading...';
    
    try {
        const response = await fetch(`${API_BASE}/api/models/load?model_name=${modelName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentModel = modelName;
            modelStatus.textContent = `Loaded: ${modelName}`;
            modelStatus.className = 'badge bg-success';
            showStatus(`Model '${modelName}' loaded successfully!`, 'success');
            
            if (stream && !isDetecting) {
                startDetection();
            }
        } else {
            throw new Error(data.error || 'Failed to load model');
        }
    } catch (error) {
        console.error('Error loading model:', error);
        showStatus('Error loading model: ' + error.message, 'danger');
        modelStatus.textContent = 'Load failed';
        modelStatus.className = 'badge bg-danger';
    } finally {
        loadModelBtn.disabled = false;
        loadModelBtn.innerHTML = 'Load Model';
    }
}

async function trainNewModel() {
    const modelName = newModelName.value.trim();
    if (!modelName) {
        showStatus('Please enter a model name', 'warning');
        return;
    }
    
    if (!confirm(`Train new model "${modelName}" with current dataset?`)) {
        return;
    }
    
    trainModelBtn.disabled = true;
    trainModelBtn.innerHTML = 'Training...';
    
    try {
        showProgress(trainProgressContainer, trainProgressBar, trainProgressText, 10, 'Initializing training...');
        trainStats.style.display = 'block';
        
        let progressInterval = setInterval(async () => {
            try {
                const progressResponse = await fetch(`${API_BASE}/api/train/progress/${modelName}`);
                const progressData = await progressResponse.json();
                
                if (progressData.success) {
                    elapsedTime.textContent = formatTime(progressData.elapsed_time || 0);
                    progressPercent.textContent = `${progressData.progress || 0}%`;
                    showProgress(trainProgressContainer, trainProgressBar, trainProgressText, 
                        progressData.progress || 10, progressData.message || 'Training in progress...');
                    
                    if (progressData.accuracy && progressData.accuracy > 0) {
                        currentAccuracy.textContent = `${(progressData.accuracy * 100).toFixed(1)}%`;
                    }
                }
            } catch (e) {
                console.log('Progress check failed:', e);
            }
        }, 2000);
        
        const response = await fetch(`${API_BASE}/api/train?model_name=${modelName}`, {
            method: 'POST'
        });
        
        clearInterval(progressInterval);
        const result = await response.json();
        
        if (result.success) {
            showProgress(trainProgressContainer, trainProgressBar, trainProgressText, 100, 'Training completed successfully!');
            
            if (result.accuracy) {
                currentAccuracy.textContent = `${(result.accuracy * 100).toFixed(1)}%`;
            }
            
            showStatus(`Model '${modelName}' trained with ${(result.accuracy * 100).toFixed(1)}% accuracy!`, 'success');
            newModelName.value = '';
            await loadModels();
            modelSelect.value = modelName;
            await loadSelectedModel();
            
            setTimeout(() => {
                hideProgress(trainProgressContainer);
                trainStats.style.display = 'none';
            }, 3000);
        } else {
            throw new Error(result.error || 'Training failed');
        }
    } catch (error) {
        console.error('Error training model:', error);
        showStatus('Training error: ' + error.message, 'danger');
        showProgress(trainProgressContainer, trainProgressBar, trainProgressText, 0, 'Error: ' + error.message);
        trainProgressBar.className = 'progress-bar bg-danger';
    } finally {
        trainModelBtn.disabled = false;
        trainModelBtn.innerHTML = 'Train New Model';
    }
}

async function uploadImages() {
    const name = personName.value.trim();
    const files = imageUpload.files;
    
    if (!name || files.length === 0) {
        showStatus('Please enter name and select images', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('person_name', name);
    
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    uploadBtn.disabled = true;
    uploadStatus.textContent = `Uploading ${files.length} image(s)...`;
    
    try {
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus(result.message, 'success');
            personName.value = '';
            imageUpload.value = '';
            uploadStatus.textContent = '';
            loadDatasetInfo();
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Error uploading images:', error);
        showStatus('Upload error: ' + error.message, 'danger');
        uploadStatus.innerHTML = `<span class="text-danger">Error: ${error.message}</span>`;
    } finally {
        uploadBtn.disabled = false;
    }
}

async function uploadAndAutoTrain() {
    const name = personName.value.trim();
    const files = imageUpload.files;
    
    if (!name || files.length === 0) {
        showStatus('Please enter name and select images', 'warning');
        return;
    }
    
    uploadAndTrainBtn.disabled = true;
    uploadBtn.disabled = true;
    
    try {
        showProgress(progressContainer, progressBar, progressText, 20, 'Uploading images...');
        
        const formData = new FormData();
        formData.append('person_name', name);
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        const uploadResponse = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        const uploadResult = await uploadResponse.json();
        
        if (!uploadResult.success) {
            throw new Error(uploadResult.error || 'Upload failed');
        }
        
        showProgress(progressContainer, progressBar, progressText, 40, 'Upload complete. Starting training...');
        uploadTrainStats.style.display = 'block';
        
        const modelName = `${name}_model_${Date.now()}`;
        
        let progressInterval = setInterval(async () => {
            try {
                const progressResponse = await fetch(`${API_BASE}/api/train/progress/${modelName}`);
                const progressData = await progressResponse.json();
                
                if (progressData.success) {
                    uploadElapsedTime.textContent = formatTime(progressData.elapsed_time || 0);
                    const totalProgress = 40 + (progressData.progress || 0) * 0.6;
                    showProgress(progressContainer, progressBar, progressText, 
                        totalProgress, progressData.message || 'Training...');
                    
                    if (progressData.accuracy && progressData.accuracy > 0) {
                        uploadAccuracy.textContent = `${(progressData.accuracy * 100).toFixed(1)}%`;
                    }
                }
            } catch (e) {
                console.log('Progress check failed:', e);
            }
        }, 2000);
        
        const trainResponse = await fetch(`${API_BASE}/api/train?model_name=${modelName}`, {
            method: 'POST'
        });
        
        clearInterval(progressInterval);
        const trainResult = await trainResponse.json();
        
        if (trainResult.success) {
            showProgress(progressContainer, progressBar, progressText, 100, 'Training complete! Loading model...');
            
            showStatus(`Successfully trained model with ${(trainResult.accuracy * 100).toFixed(1)}% accuracy!`, 'success');
            
            personName.value = '';
            imageUpload.value = '';
            await loadModels();
            await loadDatasetInfo();
            
            setTimeout(() => {
                hideProgress(progressContainer);
                uploadTrainStats.style.display = 'none';
            }, 3000);
        } else {
            throw new Error(trainResult.error || 'Training failed');
        }
    } catch (error) {
        console.error('Error in upload and train:', error);
        showStatus('Error: ' + error.message, 'danger');
        showProgress(progressContainer, progressBar, progressText, 0, 'Error: ' + error.message);
        progressBar.className = 'progress-bar bg-danger';
    } finally {
        uploadAndTrainBtn.disabled = false;
        uploadBtn.disabled = false;
    }
}

async function toggleCamera() {
    if (stream) {
        stopCamera();
        cameraToggle.textContent = 'Start Camera';
        cameraToggle.className = 'btn btn-success btn-lg';
        detectionStatus.textContent = 'Camera is off';
    } else {
        try {
            await startCamera();
            cameraToggle.textContent = 'Stop Camera';
            cameraToggle.className = 'btn btn-danger btn-lg';
            
            if (currentModel) {
                startDetection();
                detectionStatus.textContent = 'Detecting faces...';
            } else {
                detectionStatus.textContent = 'Camera active - No model loaded';
            }
        } catch (error) {
            console.error('Error accessing camera:', error);
            showStatus('Could not access camera: ' + error.message, 'danger');
        }
    }
}

async function startCamera() {
    try {
        console.log('Requesting camera access...');
        
        // Check if mediaDevices is available
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera API not supported in this browser');
        }
        
        // Get list of devices
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        console.log('Video devices found:', videoDevices.length);
        videoDevices.forEach((d, i) => console.log(`Camera ${i}:`, d.label || 'Unknown', d.deviceId));
        
        if (videoDevices.length === 0) {
            throw new Error('No camera devices found');
        }
        
        // Try default camera first
        console.log('Trying default camera...');
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 },
                audio: false 
            });
            console.log('Default camera success');
        } catch (err) {
            console.error('Default camera failed:', err.name, err.message);
            
            // Try each specific camera
            for (let i = 0; i < videoDevices.length; i++) {
                try {
                    console.log(`Trying camera ${i}:`, videoDevices[i].label);
                    stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { deviceId: videoDevices[i].deviceId },
                        audio: false 
                    });
                    console.log(`Camera ${i} success`);
                    break;
                } catch (e) {
                    console.error(`Camera ${i} failed:`, e.name, e.message);
                }
            }
        }
        
        if (!stream) {
            throw new Error('All cameras failed. Check if camera is in use by another app.');
        }
        
        video.srcObject = stream;
        console.log('Stream assigned to video element');
        
        return new Promise((resolve) => {
            video.onloadedmetadata = () => {
                console.log('Video metadata loaded');
                video.play();
                resolve();
            };
        });
        
    } catch (error) {
        console.error('Camera error:', error.name, error.message, error);
        throw error;
    }
}

function stopCamera() {
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
    
    isDetecting = false;
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        video.srcObject = null;
    }
}

function startDetection() {
    if (!currentModel) return;
    
    isDetecting = true;
    detectionInterval = setInterval(captureAndDetect, 1500);
}

async function captureAndDetect() {
    if (!stream || !isDetecting || !currentModel || isProcessing) return;
    
    isProcessing = true;
    
    try {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('file', blob, 'frame.jpg');
            
            try {
                const response = await fetch(`${API_BASE}/infer`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                updateDetectionResult(result);
                
            } catch (error) {
                console.error('Error during detection:', error);
                detectionStatus.textContent = 'Detection error: ' + error.message;
            } finally {
                isProcessing = false;
            }
        }, 'image/jpeg', 0.7);
        
    } catch (error) {
        console.error('Error capturing frame:', error);
        detectionStatus.textContent = 'Capture error: ' + error.message;
        isProcessing = false;
    }
}

function updateDetectionResult(result) {
    const confidence = result.confidence ? (result.confidence * 100).toFixed(1) : '0';
    console.log('Detection result:', result);
    
    detectionStatus.innerHTML = `
        <strong>Detected:</strong> ${result.label} 
        <span class="badge bg-info">${confidence}%</span>
    `;
    
    if (result.is_birthday_person) {
        console.log('Birthday person detected! Triggering celebration...');
        celebrateBirthday(result.label);
        detectionStatus.innerHTML += ' <span class="badge bg-success">🎉 BIRTHDAY PERSON!</span>';
    }
}

function celebrateBirthday(name) {
    const now = Date.now();
    
    // Only celebrate if 30 seconds have passed since last celebration
    if (now - lastCelebrationTime < 30000) {
        console.log('Celebration already in progress, skipping...');
        return;
    }
    
    console.log('Celebrating birthday for:', name);
    lastCelebrationTime = now;
    
    birthdayAudio.currentTime = 0;
    birthdayAudio.volume = 0.7;
    birthdayAudio.play().then(() => {
        console.log('Audio playing successfully');
        showAudioIndicator();
    }).catch(e => {
        console.error('Audio play failed:', e);
    });
    
    setTimeout(() => createBirthdayBanner(name), 100);
    setTimeout(() => createBalloons(), 200);
    setTimeout(() => createConfetti(), 300);
    setTimeout(() => createFireworks(), 400);
    setTimeout(() => createSparkles(), 500);
    setTimeout(() => createCakeAnimation(), 600);
    
    showStatus(`🎉 Happy Birthday ${name}! 🎂`, 'success');
}

function showAudioIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'audio-indicator';
    indicator.innerHTML = '🎵 Playing Birthday Song...';
    document.body.appendChild(indicator);
    
    setTimeout(() => indicator.remove(), 5000);
}

function createSparkles() {
    const sparkleEmojis = ['✨', '⭐', '🌟', '💫'];
    
    for (let i = 0; i < 20; i++) {
        setTimeout(() => {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            sparkle.textContent = sparkleEmojis[Math.floor(Math.random() * sparkleEmojis.length)];
            sparkle.style.left = Math.random() * 100 + '%';
            sparkle.style.top = Math.random() * 100 + '%';
            sparkle.style.animationDelay = (Math.random() * 0.5) + 's';
            document.body.appendChild(sparkle);
            
            setTimeout(() => {
                if (sparkle.parentNode) {
                    sparkle.remove();
                }
            }, 3000);
        }, i * 150);
    }
}

function createCakeAnimation() {
    const cake = document.createElement('div');
    cake.className = 'cake-animation';
    cake.textContent = '🎂';
    document.body.appendChild(cake);
    
    setTimeout(() => {
        if (cake.parentNode) {
            cake.remove();
        }
    }, 4000);
}

function createConfetti() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
    const container = document.body;
    
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 2 + 's';
        container.appendChild(confetti);
        
        setTimeout(() => {
            if (confetti.parentNode) {
                confetti.remove();
            }
        }, 3000);
    }
}

function createBirthdayBanner(name) {
    const banner = document.createElement('div');
    banner.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 60px 100px;
        border-radius: 30px;
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        z-index: 10000;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border: 5px solid white;
    `;
    banner.innerHTML = `
        🎉 🎂 🎈<br>
        HAPPY BIRTHDAY<br>
        <span style="font-size: 1.5em; color: #ffeb3b;">${name}!</span><br>
        🎈 🎁 🎉
    `;
    document.body.appendChild(banner);
    
    setTimeout(() => banner.remove(), 5000);
}

function createBalloons() {
    for (let i = 0; i < 8; i++) {
        setTimeout(() => {
            const balloon = document.createElement('div');
            balloon.textContent = '🎈';
            balloon.style.cssText = `
                position: fixed;
                left: ${10 + i * 11}%;
                bottom: -100px;
                font-size: 60px;
                z-index: 9998;
                animation: balloon-float ${5 + Math.random()}s ease-in forwards;
            `;
            document.body.appendChild(balloon);
            setTimeout(() => balloon.remove(), 7000);
        }, i * 200);
    }
}

function createFireworks() {
    const colors = ['#ff0844', '#ffb199', '#ffd23f', '#00d9ff', '#a259ff'];
    
    for (let i = 0; i < 3; i++) {
        setTimeout(() => {
            const x = 20 + Math.random() * 60;
            const y = 20 + Math.random() * 40;
            
            for (let j = 0; j < 30; j++) {
                const firework = document.createElement('div');
                firework.className = 'firework';
                firework.style.left = x + '%';
                firework.style.top = y + '%';
                firework.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                
                const angle = (Math.PI * 2 * j) / 30;
                const velocity = 50 + Math.random() * 50;
                firework.style.setProperty('--x', Math.cos(angle) * velocity + 'px');
                firework.style.setProperty('--y', Math.sin(angle) * velocity + 'px');
                firework.style.animation = 'firework-burst 1s ease-out forwards';
                
                document.body.appendChild(firework);
                
                setTimeout(() => {
                    if (firework.parentNode) {
                        firework.remove();
                    }
                }, 1000);
            }
        }, i * 800);
    }
}
