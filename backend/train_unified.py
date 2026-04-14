#!/usr/bin/env python3
"""
AgriVerse Unified Disease Model Training Script
Trains disease classification models with high accuracy and confidence
Supports multiple crops: Cotton, Pepper, Potato, Rice, Tomato, Banana
"""

import os
import sys
import json
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import logging
from datetime import datetime

# TensorFlow components
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0, ResNet50  
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, 
    TensorBoard, LambdaCallback
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score, 
    precision_score, recall_score, f1_score
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

CONFIG = {
    # Image settings
    "img_size": (224, 224),
    "batch_size": 32,  # Balanced - smooth gradients + reasonable speed
    "epochs": 200,     # Increased for better convergence and confidence
    "learning_rate": 0.0005,  # Slightly lower for finer-tuned predictions
    "validation_split": 0.2,
    
    # Regularization (balanced for accuracy + confidence)
    "dropout_rate": 0.4,  # Reduced from 0.5 - allows more learning
    "l2_regularization": 0.00005,  # Slightly lower - less weight penalty
    
    # Early stopping & learning rate (stage 1: frozen base)
    "patience": 20,     # Increased from 15 - more chances to improve
    "reduce_lr_factor": 0.5,
    "reduce_lr_patience": 7,  # Increased from 5 - waits longer before reducing LR
    
    # Model selection
    "base_model": "efficientnet",  # efficientnet, mobilenet, resnet50
}

# ==================== DISEASE TRANSLATIONS ====================

DISEASE_TRANSLATIONS = {
    # Cotton
    "Healthy": "ఆరోగ్యకరమైన",
    "Aphids": "చీమలు",
    "Army worm": "సేనా పురుగు",
    "Bacterial Blight": "బాక్టీరియల్ బ్లిట్",
    "Powdery Mildew": "పౌడరీ మిల్డ్యూ",
    "Target spot": "లక్ష్య స్థానం",
    
    # Pepper
    "Pepper__bell___Bacterial_spot": "మిరపకాయ బాక్టీరియల్ స్పాట్",
    "Pepper__bell___healthy": "ఆరోగ్యకరమైన మిరపకాయ",
    
    # Potato
    "Potato___Early_blight": "ఆలు ముందుగా కాలుష్యం",
    "Potato___healthy": "ఆరోగ్యకరమైన ఆలు",
    "Potato___Late_blight": "ఆలు ఆలస్యంగా కాలుష్యం",
    
    # Rice
    "Bacterial Leaf Blight": "బాక్టీరియల్ ఇల బ్లిట్",
    "Brown Spot": "బ్రౌన్ స్పాట్",
    "Healthy Rice Leaf": "ఆరోగ్యకరమైన బియ్య ఇల",
    "Leaf Blast": "ఇల బ్లాస్ట్",
    "Leaf scald": "ఇల స్కాల్డ్",
    "Sheath Blight": "కవచం బ్లిట్",
    
    # Tomato
    "Tomato___Bacterial_spot": "టమోటా బాక్టీరియల్ స్పాట్",
    "Tomato___Early_blight": "టమోటా ముందుగా కాలుష్యం",
    "Tomato___healthy": "ఆరోగ్యకరమైన టమోటా",
    "Tomato___Late_blight": "టమోటా ఆలస్యంగా కాలుష్యం",
    "Tomato___Leaf_Mold": "టమోటా ఇల పూఁఔ",
    "Tomato___Septoria_leaf_spot": "టమోటా సెప్టోరియా ఇల స్పాట్",
    "Tomato___Spider_mites Two-spotted_spider_mite": "టమోటా క్రిమి",
    "Tomato___Target_Spot": "టమోటా లక్ష్య స్థానం",
    "Tomato___Tomato_mosaic_virus": "టమోటా మోజాయిక్ వైరస్",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "టమోటా పసుపు ఇల కర్ల్ వైరస్",
}

# ==================== DATA AUGMENTATION ====================

def create_data_generators(use_augmentation=True):
    """Create training and validation data generators with aggressive augmentation"""
    
    if use_augmentation:
        train_datagen = ImageDataGenerator(
            rotation_range=25,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.25,
            horizontal_flip=True,
            vertical_flip=True,
            fill_mode='nearest',
            brightness_range=[0.8, 1.2],
            channel_shift_range=30.0,
            rescale=1./255,
            validation_split=CONFIG["validation_split"]
        )
    else:
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=CONFIG["validation_split"]
        )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    return train_datagen, val_datagen


def load_data(data_dir: str):
    """Load training and validation data with robust path resolution"""
    
    # Resolve path
    data_path = Path(data_dir)
    
    # Try multiple paths if relative
    if not data_path.exists():
        logger.info(f"⚠️  Path not found: {data_dir}")
        
        # Try relative to backend directory
        alt_path = Path(__file__).parent / data_dir
        if alt_path.exists():
            logger.info(f"✅ Found at: {alt_path}")
            data_path = alt_path
        else:
            logger.error(f"❌ Could not find dataset at: {data_dir}")
            logger.error(f"   Also tried: {alt_path}")
            raise FileNotFoundError(f"Dataset not found at {data_dir}")
    
    data_dir_str = str(data_path.absolute())
    logger.info(f"📂 Loading data from: {data_dir_str}")
    
    # Debug: List contents
    try:
        subdirs = [d for d in Path(data_dir_str).iterdir() if d.is_dir()]
        logger.info(f"   Found {len(subdirs)} class directories:")
        total_imgs = 0
        for subdir in sorted(subdirs)[:10]:  # Show first 10
            img_count = len(list(subdir.glob("*.[jp][pn]g"))) + len(list(subdir.glob("*.JPEG")))
            total_imgs += img_count
            logger.info(f"     - {subdir.name}: {img_count} images")
        if len(subdirs) > 10:
            logger.info(f"     ... and {len(subdirs) - 10} more")
        logger.info(f"   Total images found: {total_imgs}")
    except Exception as e:
        logger.error(f"   Error listing contents: {e}")
    
    # Create BOTH generators with validation_split
    train_datagen = ImageDataGenerator(
        rotation_range=25,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.25,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest',
        brightness_range=[0.8, 1.2],
        channel_shift_range=30.0,
        rescale=1./255,
        validation_split=CONFIG["validation_split"]
    )
    
    logger.info(f"📊 Creating generators with {CONFIG['batch_size']} batch size...")
    
    # Training data (from same datagen with validation_split)
    try:
        train_generator = train_datagen.flow_from_directory(
            data_dir_str,
            target_size=CONFIG["img_size"],
            batch_size=CONFIG["batch_size"],
            class_mode='categorical',
            subset='training',
            shuffle=True,
            seed=42
        )
        logger.info(f"✅ Training generator: {train_generator.samples} samples")
    except Exception as e:
        logger.error(f"❌ Error creating training generator: {e}")
        raise
    
    # Validation data (from same datagen with validation_split, no augmentation needed)
    try:
        val_generator = train_datagen.flow_from_directory(
            data_dir_str,
            target_size=CONFIG["img_size"],
            batch_size=CONFIG["batch_size"],
            class_mode='categorical',
            subset='validation',
            shuffle=False,
            seed=42
        )
        logger.info(f"✅ Validation generator: {val_generator.samples} samples")
    except Exception as e:
        logger.error(f"❌ Error creating validation generator: {e}")
        raise
    
    if train_generator.samples == 0:
        logger.error("❌ No training images found!")
        logger.error(f"   Expected structure: {data_dir_str}/[class_name]/[image.jpg|png]")
        raise ValueError(f"No images found in {data_dir_str}")
    
    logger.info(f"✅ Loaded {train_generator.samples} training samples")
    logger.info(f"✅ Loaded {val_generator.samples} validation samples")
    logger.info(f"📊 Classes: {list(train_generator.class_indices.keys())}")
    
    return train_generator, val_generator


def create_model(num_classes: int, base_model_name: str = "efficientnet"):
    """Create transfer learning model with high accuracy architecture"""
    
    logger.info(f"🏗️ Creating {base_model_name} model with {num_classes} classes")
    
    # Select base model with robust weight loading
    try:
        if base_model_name.lower() == "efficientnet":
            logger.info("📦 Loading EfficientNetB0 (may take 1-2 minutes on first run)...")
            base = EfficientNetB0(
                input_shape=(224, 224, 3), 
                include_top=False, 
                weights='imagenet'
            )
        elif base_model_name.lower() == "resnet50":
            logger.info("📦 Loading ResNet50 (may take 1-2 minutes on first run)...")
            base = ResNet50(
                input_shape=(224, 224, 3), 
                include_top=False, 
                weights='imagenet'
            )
        else:  # MobileNetV2 (default)
            logger.info("📦 Loading MobileNetV2...")
            base = MobileNetV2(
                input_shape=(224, 224, 3), 
                include_top=False, 
                weights='imagenet'
            )
        logger.info("✅ Pre-trained weights loaded successfully")
    except Exception as e:
        # Fallback: Load without pre-trained weights
        logger.warning(f"⚠️  Could not load pre-trained weights: {type(e).__name__}")
        logger.info("📦 Loading model without pre-trained weights (training from scratch)...")
        
        if base_model_name.lower() == "efficientnet":
            base = EfficientNetB0(
                input_shape=(224, 224, 3), 
                include_top=False, 
                weights=None
            )
        elif base_model_name.lower() == "resnet50":
            base = ResNet50(
                input_shape=(224, 224, 3), 
                include_top=False, 
                weights=None
            )
        else:
            base = MobileNetV2(
                input_shape=(224, 224, 3), 
                include_top=False, 
                weights=None
            )
        logger.warning("⚠️  Model will train from random initialization (slower convergence)")
    
    # Freeze base model layers
    base.trainable = False
    
    # Build custom head
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(CONFIG["l2_regularization"]))(x)
    x = Dropout(CONFIG["dropout_rate"])(x)
    x = BatchNormalization()(x)
    x = Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(CONFIG["l2_regularization"]))(x)
    x = Dropout(CONFIG["dropout_rate"])(x)
    x = BatchNormalization()(x)
    output = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=output)
    
    # Compile
    optimizer = Adam(learning_rate=CONFIG["learning_rate"])
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    logger.info("✅ Model created and compiled")
    return model, base


def train_model(model, base, train_gen, val_gen, task_id: str):
    """Two-stage training: base frozen + fine-tuning"""
    
    logger.info("🚀 Stage 1: Training with frozen base model")
    
    # Callbacks
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=CONFIG["patience"],
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=CONFIG["reduce_lr_factor"],
        patience=CONFIG["reduce_lr_patience"],
        min_lr=0.00001,
        verbose=1
    )
    
    model_checkpoint = ModelCheckpoint(
        f'app/models/{task_id}_disease_model_stage1.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
    
    # Stage 1: Train with frozen base
    history_stage1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=CONFIG["epochs"],
        callbacks=[early_stop, reduce_lr, model_checkpoint],
        verbose=1
    )
    
    logger.info("✅ Stage 1 complete")
    logger.info("🔓 Stage 2: Fine-tuning with unfrozen base layers (improves confidence)")
    
    # Unfreeze base layers for fine-tuning
    base.trainable = True
    
    # Re-compile with VERY low learning rate for precision
    # Lower LR = smaller steps = more precise weight adjustments = higher confidence
    optimizer = Adam(learning_rate=CONFIG["learning_rate"] / 20)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Stage 2: Fine-tune (longer patience for confidence improvement)
    early_stop_2 = EarlyStopping(
        monitor='val_loss',
        patience=CONFIG["patience"],  # Same as stage 1 for thorough fine-tuning
        restore_best_weights=True
    )
    
    reduce_lr_2 = ReduceLROnPlateau(
        monitor='val_loss',
        factor=CONFIG["reduce_lr_factor"],
        patience=CONFIG["reduce_lr_patience"],
        min_lr=0.000001,  # Very low floor for precision
        verbose=1
    )
    
    history_stage2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=CONFIG["epochs"],
        callbacks=[early_stop_2, reduce_lr_2],
        initial_epoch=len(history_stage1.history['loss']),
        verbose=1
    )
    
    logger.info("✅ Training complete")
    
    return model, history_stage1, history_stage2


def evaluate_model(model, val_gen, task_id: str) -> Dict:
    """Evaluate model and generate metrics including confidence analysis"""
    
    logger.info("📊 Evaluating model with confidence metrics...")
    
    # Get predictions
    val_gen.reset()
    y_true = val_gen.classes
    y_pred_probs = model.predict(val_gen, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    # Get max prediction confidence for each sample
    max_confidences = np.max(y_pred_probs, axis=1)
    
    # Calculate accuracy metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # Calculate confidence metrics
    avg_confidence = np.mean(max_confidences)
    std_confidence = np.std(max_confidences)
    max_confidence = np.max(max_confidences)
    min_confidence = np.min(max_confidences)
    
    # Percentage of predictions with high confidence (>0.8)
    high_confidence_count = np.sum(max_confidences > 0.8)
    high_confidence_pct = (high_confidence_count / len(max_confidences)) * 100
    
    # Accuracy for high-confidence predictions
    correct_predictions = (y_true == y_pred)
    high_conf_correct = np.sum(correct_predictions & (max_confidences > 0.8))
    high_conf_total = np.sum(max_confidences > 0.8)
    high_conf_accuracy = (high_conf_correct / high_conf_total * 100) if high_conf_total > 0 else 0
    
    # Log all metrics
    logger.info("=" * 60)
    logger.info("📊 ACCURACY METRICS:")
    logger.info(f"  ✅ Overall Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"  ✅ Precision:         {precision:.4f}")
    logger.info(f"  ✅ Recall:            {recall:.4f}")
    logger.info(f"  ✅ F1 Score:          {f1:.4f}")
    logger.info("=" * 60)
    logger.info("🎯 CONFIDENCE METRICS:")
    logger.info(f"  ✅ Average Confidence: {avg_confidence:.4f}")
    logger.info(f"  ✅ Std Dev:            {std_confidence:.4f}")
    logger.info(f"  ✅ Min Confidence:     {min_confidence:.4f}")
    logger.info(f"  ✅ Max Confidence:     {max_confidence:.4f}")
    logger.info(f"  ✅ High Confidence %:  {high_confidence_pct:.1f}% (>0.8)")
    logger.info(f"  ✅ High Conf Accuracy: {high_conf_accuracy:.1f}%")
    logger.info("=" * 60)
    
    # Confidence thresholds analysis
    logger.info("🎯 PREDICTIONS BY CONFIDENCE THRESHOLD:")
    for threshold in [0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]:
        above_threshold = np.sum(max_confidences >= threshold)
        pct = (above_threshold / len(max_confidences)) * 100
        correct_above = np.sum(correct_predictions & (max_confidences >= threshold))
        acc_above = (correct_above / above_threshold * 100) if above_threshold > 0 else 0
        logger.info(f"  {threshold:.2f}: {above_threshold:4d} predictions ({pct:5.1f}%) | "
                   f"Accuracy: {acc_above:.1f}%")
    logger.info("=" * 60)
    
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Classification report
    report = classification_report(
        y_true, y_pred,
        target_names=list(val_gen.class_indices.keys()),
        output_dict=True
    )
    
    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
        # Confidence metrics for high-quality predictions
        'avg_confidence': float(avg_confidence),
        'std_confidence': float(std_confidence),
        'min_confidence': float(min_confidence),
        'max_confidence': float(max_confidence),
        'high_confidence_percentage': float(high_confidence_pct),
        'high_confidence_accuracy': float(high_conf_accuracy),
    }

    
    return metrics


def save_training_results(model, history_s1, history_s2, metrics, label_map, task_id: str):
    """Save model, metrics, and visualizations"""
    
    model_dir = Path("app/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save model
    model_path = model_dir / f"{task_id}_disease_model.h5"
    model.save(str(model_path))
    logger.info(f"💾 Model saved: {model_path}")
    
    # Save label map
    label_path = model_dir / f"{task_id}_label_map.json"
    with open(label_path, 'w', encoding='utf-8') as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Label map saved: {label_path}")
    
    # Save metrics
    metrics_path = model_dir / f"{task_id}_training_summary.json"
    summary = {
        "task_id": task_id,
        "timestamp": timestamp,
        "model_config": CONFIG,
        "metrics": metrics,
        "training_epochs": len(history_s1.history['loss']) + len(history_s2.history['loss'])
    }
    with open(metrics_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"💾 Summary saved: {metrics_path}")
    
    # Plot training history
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Accuracy
    axes[0, 0].plot(history_s1.history['accuracy'], label='Stage1 Train')
    axes[0, 0].plot(history_s1.history['val_accuracy'], label='Stage1 Val')
    if history_s2.history['accuracy']:
        axes[0, 0].plot(
            range(len(history_s1.history['accuracy']), 
                  len(history_s1.history['accuracy']) + len(history_s2.history['accuracy'])),
            history_s2.history['accuracy'], label='Stage2 Train'
        )
        axes[0, 0].plot(
            range(len(history_s1.history['accuracy']),
                  len(history_s1.history['accuracy']) + len(history_s2.history['accuracy'])),
            history_s2.history['val_accuracy'], label='Stage2 Val'
        )
    axes[0, 0].set_title('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid()
    
    # Loss
    axes[0, 1].plot(history_s1.history['loss'], label='Stage1 Train')
    axes[0, 1].plot(history_s1.history['val_loss'], label='Stage1 Val')
    if history_s2.history['loss']:
        axes[0, 1].plot(
            range(len(history_s1.history['loss']),
                  len(history_s1.history['loss']) + len(history_s2.history['loss'])),
            history_s2.history['loss'], label='Stage2 Train'
        )
        axes[0, 1].plot(
            range(len(history_s1.history['loss']),
                  len(history_s1.history['loss']) + len(history_s2.history['loss'])),
            history_s2.history['val_loss'], label='Stage2 Val'
        )
    axes[0, 1].set_title('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid()
    
    # Precision & Recall
    if 'precision' in history_s1.history:
        axes[1, 0].plot(history_s1.history['precision'], label='Stage1 Train Precision')
        axes[1, 0].plot(history_s1.history['recall'], label='Stage1 Train Recall')
        axes[1, 0].set_title('Precision & Recall')
        axes[1, 0].legend()
        axes[1, 0].grid()
    
    # Final metrics
    axes[1, 1].axis('off')
    metrics_text = f"""
    Final Metrics:
    Accuracy:  {metrics['accuracy']:.4f}
    Precision: {metrics['precision']:.4f}
    Recall:    {metrics['recall']:.4f}
    F1 Score:  {metrics['f1']:.4f}
    """
    axes[1, 1].text(0.5, 0.5, metrics_text, ha='center', va='center', fontsize=12)
    
    plt.tight_layout()
    plot_path = model_dir / f"{task_id}_training_plots.png"
    plt.savefig(str(plot_path), dpi=100, bbox_inches='tight')
    logger.info(f"📈 Plot saved: {plot_path}")
    plt.close()


def validate_dataset(data_dir: str) -> bool:
    """Validate dataset structure with better error messages"""
    data_path = Path(data_dir)
    
    # Try multiple paths if relative
    if not data_path.exists():
        logger.info(f"⚠️  Path not found: {data_dir}")
        
        # Try relative to backend directory
        alt_path = Path(__file__).parent / data_dir
        if alt_path.exists():
            logger.info(f"✅ Found at: {alt_path}")
            data_path = alt_path
        else:
            logger.error(f"❌ Dataset directory not found")
            logger.error(f"   Tried: {Path(data_dir).absolute()}")
            logger.error(f"   Tried: {alt_path}")
            return False
    
    classes = [d for d in data_path.iterdir() if d.is_dir()]
    
    if not classes:
        logger.error(f"❌ No class directories found in {data_path}")
        logger.error(f"   Expected structure: {data_path}/[class_name]/")
        return False
    
    total_images = 0
    for class_dir in classes:
        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpeg"))
        if images:
            logger.info(f"  ✓ {class_dir.name}: {len(images)} images")
            total_images += len(images)
        else:
            logger.warning(f"  ⚠️  {class_dir.name}: 0 images (empty class)")
    
    if total_images == 0:
        logger.error(f"❌ No images found in any class directory")
        return False
    
    if total_images < 100:
        logger.warning(f"⚠️  Only {total_images} images found (recommended >= 100)")
    
    logger.info(f"✅ Dataset valid: {len(classes)} classes, {total_images} total images")
    return total_images >= 10  # Lowered minimum for small testing datasets


def main():
    """Main training pipeline"""
    parser = argparse.ArgumentParser(description="Train AgriVerse disease models")
    parser.add_argument("--task", default="archive", help="Task ID (cotton, rice, tomato, etc.)")
    parser.add_argument("--data_dir", default="archive/dataset", help="Dataset directory")
    parser.add_argument("--base_model", default="efficientnet", help="Base model (efficientnet, mobilenet, resnet50)")
    
    args = parser.parse_args()
    
    CONFIG["base_model"] = args.base_model
    task_id = args.task.lower()
    data_dir = args.data_dir
    
    logger.info("=" * 80)
    logger.info(f"🌾 AgriVerse Disease Detection Model Training")
    logger.info(f"Task: {task_id} | Data: {data_dir} | Base: {args.base_model}")
    logger.info("=" * 80)
    
    # Validate dataset
    if not validate_dataset(data_dir):
        logger.error("Dataset validation failed")
        return False
    
    # Load data
    train_gen, val_gen = load_data(data_dir)
    
    # Create label map
    label_map = {}
    for idx, class_name in enumerate(sorted(train_gen.class_indices.keys())):
        label_map[str(idx)] = {
            "en": class_name,
            "hi": DISEASE_TRANSLATIONS.get(class_name, class_name),
            "te": DISEASE_TRANSLATIONS.get(class_name, class_name),
        }
    
    # Create model
    model, base = create_model(train_gen.num_classes, args.base_model)
    model.summary()
    
    # Train
    trained_model, hist_s1, hist_s2 = train_model(model, base, train_gen, val_gen, task_id)
    
    # Evaluate
    metrics = evaluate_model(trained_model, val_gen, task_id)
    
    # Save
    save_training_results(trained_model, hist_s1, hist_s2, metrics, label_map, task_id)
    
    logger.info("=" * 80)
    logger.info(f"🎉 Training successful!")
    logger.info(f"✅ Final Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"✅ Final F1 Score: {metrics['f1']:.4f}")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
