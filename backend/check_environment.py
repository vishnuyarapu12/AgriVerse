#!/usr/bin/env python3
"""
AgriVerse Environment Diagnostics
Check TensorFlow, Keras, and GPU setup
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("🔍 AgriVerse Environment Diagnostics")
print("="*70 + "\n")

# Check Python version
print(f"✓ Python Version: {sys.version.split()[0]}")
if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    print("  ✅ Python 3.9+ (supported)")
else:
    print("  ⚠️  Python < 3.9 (may have compatibility issues)")

print()

# Check TensorFlow
try:
    import tensorflow as tf
    print(f"✓ TensorFlow: {tf.__version__}")
    
    if hasattr(tf, '__version__'):
        major, minor, patch = tf.__version__.split('.')[:3]
        major, minor = int(major), int(minor)
        if major >= 2 and minor >= 10:
            print("  ✅ TensorFlow 2.10+ (recommended)")
        elif major >= 2 and minor >= 8:
            print("  ✅ TensorFlow 2.8+ (compatible)")
        else:
            print(f"  ⚠️  TensorFlow {tf.__version__} (consider upgrading)")
except ImportError as e:
    print(f"❌ TensorFlow not installed: {e}")
    print("  Install with: pip install tensorflow")

print()

# Check Keras
try:
    import keras
    print(f"✓ Keras: {keras.__version__}")
except Exception as e:
    print(f"⚠️  Keras issue: {e}")

print()

# Check GPU
try:
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✓ GPU Detected: {len(gpus)} GPU(s)")
        for i, gpu in enumerate(gpus):
            print(f"  - {gpu}")
        print("  ✅ GPU acceleration enabled (training will be fast!)")
    else:
        print("⚠️  No GPU detected - training will use CPU")
        print("  Training will be slower but still works")
except Exception as e:
    print(f"⚠️  GPU check failed: {e}")

print()

# Check key packages
packages = {
    'numpy': 'numpy',
    'PIL': 'Pillow',
    'sklearn': 'scikit-learn',
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
}

print("📦 Required Packages:")
for pkg_import, pkg_name in packages.items():
    try:
        mod = __import__(pkg_import)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✓ {pkg_name}: {version}")
    except ImportError:
        print(f"  ❌ {pkg_name}: NOT INSTALLED")

print()

# Test model creation
print("🧪 Testing Model Creation...")
try:
    import tensorflow as tf
    from tensorflow.keras.applications import EfficientNetB0
    
    logger.info("  Creating test model...")
    model = EfficientNetB0(input_shape=(224, 224, 3), include_top=False, weights=None)
    print(f"  ✅ Model creation successful")
    print(f"     Parameters: {model.count_params():,}")
except Exception as e:
    print(f"  ❌ Model creation failed: {type(e).__name__}: {str(e)[:80]}")
    print("     This may affect training")

print()

# Test data loading
print("🧪 Testing Data Loading...")
try:
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    datagen = ImageDataGenerator(rescale=1./255)
    print("  ✅ Data generator created successfully")
except Exception as e:
    print(f"  ❌ Data loading failed: {e}")

print()

# Test training (mini)
print("🧪 Testing Training Loop...")
try:
    import tensorflow as tf
    import numpy as np
    
    logger.info("  Starting mini training...")
    
    # Tiny model for testing
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation='relu', input_shape=(100,)),
        tf.keras.layers.Dense(2, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    # Dummy data
    X = np.random.randn(20, 100).astype('float32')
    y = np.random.randint(0, 2, (20, 2)).astype('float32')
    
    # Train for 1 epoch
    model.fit(X, y, epochs=1, verbose=0, batch_size=4)
    print("  ✅ Training loop successful")
except Exception as e:
    print(f"  ❌ Training failed: {type(e).__name__}: {str(e)[:80]}")

print()
print("="*70)
print("Diagnostics Complete!")
print("="*70)

print("""
💡 Next Steps:
1. If all checks pass: Ready to train!
   python train_unified.py --task tomato --data_dir ../archive/dataset/Tomato

2. If GPU check failed but you have GPU:
   pip install tensorflow-gpu

3. If model creation failed:
   pip install --upgrade tensorflow keras

4. If any package is missing:
   pip install -r requirements.txt

""")
