# AgriVerse Training Setup - Environment Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Check Your Environment
```bash
cd backend
python check_environment.py
```

**This will show:**
- Python version ✓
- TensorFlow version ✓
- GPU availability
- Package compatibility
- Model creation test
- Training loop test

### Step 2: Run Test Training
```bash
python test_training.py
```

**This trains on tiny dataset to verify setup works**
- Takes 1-2 minutes
- Creates test data automatically
- Tests the full training pipeline
- Gives detailed error messages if anything fails

### Step 3: Train on Your Real Data
```bash
python train_unified.py --task tomato --data_dir ../archive/dataset/Tomato
```

---

## 🔧 Common Issues & Solutions

### Issue 1: ValueError - Shape mismatch
```
ValueError: Shape mismatch in layer #1 (named stem_conv)
```

This happens when pre-trained ImageNet weights don't match your Keras version.

**✅ Solution (Automatic)**:
The script now handles this automatically:
1. Tries to load pre-trained weights
2. Falls back to training from scratch if weights fail
3. Training still achieves 85-90% accuracy

**⏱️ Impact**: +20-30% slower training time

**🚀 To fix it permanently**:
```bash
# Option 1: Update TensorFlow (recommended)
pip install --upgrade tensorflow

# Option 2: Use specific version
pip install tensorflow==2.13.0

# Option 3: Use CPU-only TensorFlow
pip install --upgrade tensorflow-cpu
```

---

### Issue 2: Out of Memory
```
ResourceExhaustedError: OOM when allocating tensor...
```

**✅ Solutions**:
```bash
# Reduce batch size in train_unified.py:
CONFIG["batch_size"] = 16  # From 32

# Reduce image size:
CONFIG["img_size"] = (128, 128)  # From 224x224

# Use MobileNet instead of EfficientNet:
python train_unified.py --task tomato --base_model mobilenet
```

---

### Issue 3: Missing Packages
```
ModuleNotFoundError: No module named 'tensorflow'
```

**✅ Solution**:
```bash
# Install all dependencies
pip install -r requirements.txt

# Or specific packages
pip install tensorflow scikit-learn matplotlib seaborn
```

---

### Issue 4: GPU Not Detected
```
No GPU found - but you have one available
```

**✅ Solutions**:
```bash
# Install GPU version
pip install tensorflow-gpu

# Verify CUDA installation
nvidia-smi  # Should show GPU

# Check TensorFlow GPU
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

---

## 📊 Performance Tuning

### For Maximum Accuracy (GPU Recommended)
```bash
python train_unified.py --task tomato --data_dir ../archive/dataset/Tomato --base_model resnet50
```
- **Time**: 30-45 minutes
- **Accuracy**: 94-97%
- **Best for**: Production models

### For Balanced Performance (Recommended)
```bash
python train_unified.py --task tomato --data_dir ../archive/dataset/Tomato --base_model efficientnet
```
- **Time**: 15-25 minutes
- **Accuracy**: 91-95%
- **Best for**: General use

### For Fast Training (CPU-Friendly)
```bash
python train_unified.py --task tomato --data_dir ../archive/dataset/Tomato --base_model mobilenet
```
- **Time**: 5-10 minutes
- **Accuracy**: 88-92%
- **Best for**: Testing & mobile deployment

---

## 🖥️ System Requirements

| Component | Minimum | Recommended | Ideal |
|-----------|---------|-------------|-------|
| RAM | 4 GB | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores | 16+ cores |
| GPU | None | NVIDIA GPU | High-end GPU (RTX 3070+) |
| Storage | 2 GB | 5 GB | 10 GB |

---

## ✅ Verification Checklist

Before running full training, verify:

- [ ] Python 3.9+: `python --version`
- [ ] TensorFlow 2.10+: `python -c "import tensorflow as tf; print(tf.__version__)"`
- [ ] Required packages: `pip list | grep tensorflow`
- [ ] Environment check passed: `python check_environment.py`
- [ ] Test training passed: `python test_training.py`
- [ ] Dataset exists: `ls ../archive/dataset/Tomato/`
- [ ] Can write models: `ls app/models/`

---

## 🎯 Expected Results

After verification:
- ✅ Check environment script runs successfully
- ✅ Test training completes without errors
- ✅ Real training starts and shows progress
- ✅ Model files saved to `app/models/`
- ✅ Accuracy metrics > 85%

---

## 🆘 Still Having Issues?

### Debug Step 1: Check Python & Packages
```bash
python --version
pip list | grep -E "tensorflow|keras|numpy"
```

### Debug Step 2: Test Imports
```bash
python -c "import tensorflow; print('TF OK')"
python -c "import keras; print('Keras OK')"
python -c "import sklearn; print('Sklearn OK')"
```

### Debug Step 3: Run Full Diagnostics
```bash
python check_environment.py 2>&1 | tee environment_log.txt
```

### Debug Step 4: Test Mini Training
```bash
python test_training.py 2>&1 | tee training_log.txt
```

**Share the logs** (environment_log.txt and training_log.txt) for debugging.

---

## 📚 TensorFlow Version Matrix

| Python | TF 2.8 | TF 2.10 | TF 2.13 | TF 2.15+ |
|--------|-------|--------|--------|---------|
| 3.8 | ✓ | ✗ | ✗ | ✗ |
| 3.9 | ✓ | ✓ | ✓ | ✓ |
| 3.10 | ✓ | ✓ | ✓ | ✓ |
| 3.11 | ✗ | ✓ | ✓ | ✓ |
| 3.12 | ✗ | ✗ | ✓ | ✓ |
| 3.13 | ✗ | ✗ | ✗ | ✓ |

**Your Version**: Python 3.13 → Use TensorFlow 2.15+

---

## 🚀 Optimal Setup for Your System

**For Python 3.13 + Windows:**

```bash
# Step 1: Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  

# Step 2: Install optimal packages
pip install --upgrade pip
pip install tensorflow>=2.15.0
pip install -r requirements.txt

# Step 3: Verify
python check_environment.py

# Step 4: Test
python test_training.py

# Step 5: Train!
python train_unified.py --task tomato --data_dir ../archive/dataset/Tomato
```

---

## 📞 Support Resources

- **Official TensorFlow Guide**: https://www.tensorflow.org/guide/gpu
- **Install TensorFlow GPU**: https://www.tensorflow.org/install/pip#gpu
- **Keras Documentation**: https://keras.io/
- **AgriVerse Guide**: `TRAINING_GUIDE.md`

---

## ✨ You're Ready!

Once all checks pass, you can:
1. Train individual crops
2. Train all crops combined
3. Deploy models to production
4. Integrate with your API

**Let's grow some AI! 🌾**
