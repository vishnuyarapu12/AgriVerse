#!/usr/bin/env python3
"""
AgriVerse Rice Disease Model Training Script
Production-ready training script for rice disease classification
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Dict, Tuple, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "data_dir": "datasets/rice_leaf_diseases",
    "model_dir": "app/models",
    "img_size": (224, 224),
    "batch_size": 16,
    "epochs": 50,
    "learning_rate": 0.001,
    "validation_split": 0.2,
    "patience": 10,
    "base_model": "mobilenet"
}

# Rice disease translations
DISEASE_TRANSLATIONS = {
    "Bacterial leaf blight": "ബാക്ടീരിയൽ ഇല ബ്ലൈറ്റ്",
    "Brown spot": "ബ്രൗൺ സ്പോട്ട്", 
    "Leaf smut": "ഇല സ്മട്ട്"
}

def validate_dataset() -> bool:
    """Validate that the dataset exists and has proper structure"""
    data_dir = Path(CONFIG["data_dir"])
    
    if not data_dir.exists():
        logger.error(f"Dataset directory not found: {data_dir}")
        return False
    
    # Check for disease folders
    disease_folders = []
    total_images = 0
    
    for item in data_dir.iterdir():
        if item.is_dir():
            image_files = list(item.glob("*.jpg")) + list(item.glob("*.jpeg")) + list(item.glob("*.png"))
            if len(image_files) > 0:
                disease_folders.append(item.name)
                total_images += len(image_files)
                logger.info(f"Found {len(image_files)} images in '{item.name}'")
            else:
                logger.warning(f"No images found in '{item.name}'")
    
    if len(disease_folders) == 0:
        logger.error("No valid disease folders found in dataset")
        return False
    
    logger.info(f"Dataset validation successful:")
    logger.info(f"  - Disease classes: {len(disease_folders)}")
    logger.info(f"  - Total images: {total_images}")
    logger.info(f"  - Classes: {disease_folders}")
    
    return True

def create_data_generators():
    """Create data generators with augmentation"""
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        shear_range=0.2,
        fill_mode='nearest',
        validation_split=CONFIG["validation_split"]
    )
    
    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=CONFIG["validation_split"]
    )
    
    return train_datagen, val_datagen

def load_data():
    """Load and prepare the dataset"""
    train_datagen, val_datagen = create_data_generators()
    
    # Create data generators
    train_generator = train_datagen.flow_from_directory(
        CONFIG["data_dir"],
        target_size=CONFIG["img_size"],
        batch_size=CONFIG["batch_size"],
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        CONFIG["data_dir"],
        target_size=CONFIG["img_size"],
        batch_size=CONFIG["batch_size"],
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    # Create label mapping
    class_names = sorted(list(train_generator.class_indices.keys()))
    label_map = {}
    
    for idx, class_name in enumerate(class_names):
        label_map[str(idx)] = {
            "en": class_name,
            "hi": class_name,  # Fallback to English
            "ml": DISEASE_TRANSLATIONS.get(class_name, class_name)
        }
    
    # Save label mapping
    model_dir = Path(CONFIG["model_dir"])
    model_dir.mkdir(exist_ok=True)
    
    with open(model_dir / "label_map.json", "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Label mapping saved with {len(class_names)} classes")
    
    return train_generator, val_generator, label_map

def create_model(num_classes: int) -> Model:
    """Create CNN model using transfer learning"""
    try:
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(*CONFIG["img_size"], 3)
        )
    except Exception as e:
        logger.warning(f"Failed to load pre-trained weights: {e}")
        base_model = MobileNetV2(
            weights=None,
            include_top=False,
            input_shape=(*CONFIG["img_size"], 3)
        )
    
    # Freeze base model layers initially
    base_model.trainable = False
    
    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=CONFIG["learning_rate"]),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    logger.info(f"Model created with {len(model.layers)} layers")
    return model

def train_model(model: Model, train_generator, val_generator):
    """Train the model with callbacks"""
    model_dir = Path(CONFIG["model_dir"])
    
    # Define callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            patience=CONFIG["patience"],
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=model_dir / "rice_disease_model.h5",
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train model
    logger.info("Starting model training...")
    history = model.fit(
        train_generator,
        epochs=CONFIG["epochs"],
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Fine-tuning phase
    logger.info("Starting fine-tuning...")
    # Find the actual base model (MobileNetV2) in the model layers
    base_model = None
    for layer in model.layers:
        if hasattr(layer, 'layers') and len(layer.layers) > 0:
            base_model = layer
            break
    
    if base_model is None:
        logger.warning("Could not find base model for fine-tuning, skipping...")
        return model, history, None
    
    base_model.trainable = True
    
    # Fine-tune from this layer onwards
    fine_tune_at = len(base_model.layers) // 3
    
    # Freeze all the layers before the `fine_tune_at` layer
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False
    
    # Recompile with lower learning rate for fine-tuning
    model.compile(
        optimizer=Adam(learning_rate=CONFIG["learning_rate"] / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Continue training with fine-tuning
    history_fine = model.fit(
        train_generator,
        epochs=CONFIG["epochs"] // 2,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    return model, history, history_fine

def evaluate_model(model: Model, val_generator):
    """Evaluate model performance"""
    logger.info("Evaluating model...")
    
    # Get predictions
    val_generator.reset()
    predictions = model.predict(val_generator, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    
    # Get true labels
    true_classes = val_generator.classes
    class_labels = list(val_generator.class_indices.keys())
    
    # Calculate metrics
    accuracy = np.mean(predicted_classes == true_classes)
    
    # Classification report
    report = classification_report(
        true_classes, 
        predicted_classes, 
        target_names=class_labels,
        output_dict=True
    )
    
    logger.info(f"Validation Accuracy: {accuracy:.4f}")
    
    # Log per-class metrics
    for class_name in class_labels:
        if class_name in report:
            precision = report[class_name]['precision']
            recall = report[class_name]['recall']
            f1 = report[class_name]['f1-score']
            logger.info(f"{class_name}: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
    
    return {
        "accuracy": accuracy,
        "classification_report": report
    }

def save_training_results(model: Model, history, history_fine, metrics: Dict, label_map: Dict, 
                         train_generator, val_generator):
    """Save training results and summary"""
    model_dir = Path(CONFIG["model_dir"])
    
    # Save final model
    final_model_path = model_dir / "rice_disease_model.h5"
    model.save(final_model_path)
    logger.info(f"Final model saved to: {final_model_path}")
    
    # Save training summary
    training_summary = {
        "config": CONFIG,
        "metrics": metrics,
        "label_map": label_map,
        "training_samples": train_generator.samples,
        "validation_samples": val_generator.samples,
        "num_classes": train_generator.num_classes,
        "training_completed": True
    }
    
    summary_path = model_dir / "training_summary.json"
    with open(summary_path, "w") as f:
        json.dump(training_summary, f, indent=2)
    logger.info(f"Training summary saved to: {summary_path}")
    
    # Create plots
    try:
        plot_training_history(history, history_fine)
        plot_confusion_matrix(model, val_generator)
    except Exception as e:
        logger.warning(f"Could not create plots: {e}")

def plot_training_history(history, history_fine=None):
    """Plot training history"""
    model_dir = Path(CONFIG["model_dir"])
    
    plt.figure(figsize=(15, 5))
    
    # Plot accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    if history_fine:
        plt.plot(history_fine.history['accuracy'], label='Fine-tuning Training Accuracy')
        plt.plot(history_fine.history['val_accuracy'], label='Fine-tuning Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    # Plot loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    if history_fine:
        plt.plot(history_fine.history['loss'], label='Fine-tuning Training Loss')
        plt.plot(history_fine.history['val_loss'], label='Fine-tuning Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(model_dir / "training_history.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.info("Training history plot saved")

def plot_confusion_matrix(model: Model, val_generator):
    """Plot confusion matrix"""
    model_dir = Path(CONFIG["model_dir"])
    
    val_generator.reset()
    predictions = model.predict(val_generator, verbose=0)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = val_generator.classes
    
    cm = confusion_matrix(true_classes, predicted_classes)
    class_labels = list(val_generator.class_indices.keys())
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_labels, yticklabels=class_labels)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(model_dir / "confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.info("Confusion matrix plot saved")

def main():
    """Main training pipeline"""
    logger.info("🌾 Starting AgriVerse Rice Disease Model Training")
    logger.info("=" * 60)
    
    try:
        # Validate dataset
        if not validate_dataset():
            logger.error("Dataset validation failed. Training aborted.")
            return False
        
        # Load data
        train_generator, val_generator, label_map = load_data()
        
        # Create model
        model = create_model(train_generator.num_classes)
        model.summary()
        
        # Train model
        trained_model, history, history_fine = train_model(model, train_generator, val_generator)
        
        # Evaluate model
        metrics = evaluate_model(trained_model, val_generator)
        
        # Save results
        save_training_results(trained_model, history, history_fine, metrics, label_map, 
                             train_generator, val_generator)
        
        logger.info("=" * 60)
        logger.info("🎉 Training completed successfully!")
        logger.info(f"Final validation accuracy: {metrics['accuracy']:.4f}")
        logger.info("Model ready for production use")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        logger.exception("Full error traceback:")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
