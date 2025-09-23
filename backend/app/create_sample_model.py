"""
Create a sample CNN model for crop disease detection
This is for demonstration purposes - in production, train with real data
"""
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical

def create_sample_model():
    """Create a sample CNN model for crop disease detection"""
    
    # Define number of classes based on label_map.json
    with open(os.path.join(os.path.dirname(__file__), "models", "label_map.json"), "r") as f:
        label_map = json.load(f)
    
    num_classes = len(label_map)
    
    # Create a simple CNN model
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Create some dummy training data for demonstration
    # In real scenario, load actual crop disease images
    print("Creating sample training data...")
    X_train = np.random.random((100, 224, 224, 3))  # 100 sample images
    y_train = np.random.randint(0, num_classes, 100)
    y_train = to_categorical(y_train, num_classes)
    
    # Train for a few epochs (just for demo)
    print("Training sample model...")
    model.fit(X_train, y_train, epochs=3, batch_size=16, verbose=1)
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), "models", "disease_model.h5")
    model.save(model_path)
    print(f"Model saved to: {model_path}")
    
    return model

if __name__ == "__main__":
    # Ensure models directory exists
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    create_sample_model()
    print("✅ Sample model created successfully!")