import numpy as np
import os

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Generate a sample 128-dimensional face embedding (typical for face_recognition library)
# This is just a random embedding for demonstration purposes
# In a real application, this would be the mean embedding of PersonA's face images
sample_embedding = np.random.rand(128).astype(np.float64)

# Save the embedding
np.save('models/personA_mean_embedding.npy', sample_embedding)

print("Sample personA_mean_embedding.npy created successfully!")
print(f"Embedding shape: {sample_embedding.shape}")
print(f"Embedding saved to: models/personA_mean_embedding.npy")