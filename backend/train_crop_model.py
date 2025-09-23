"""
Crop Type Classification Training Script

Trains a MobileNetV2 transfer-learning classifier to detect the top 5 crops
commonly cultivated in Kerala and South Indian states.

Expected dataset layout (example):
datasets/crops/
  Banana/
    img1.jpg, img2.jpg, ...
  Coconut/
  Pepper/
  Rice/
  Rubber/

Outputs:
- app/models/crop_model.h5
- app/models/crop_label_map.json
- app/models/crop_training_summary.json
- app/models/crop_training_history.png, crop_confusion_matrix.png
"""

import os
import json
import numpy as np
from pathlib import Path
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "data_dir": "datasets/crops",  # from backend/ working dir
    "model_dir": "app/models",
    "img_size": (224, 224),
    "batch_size": 16,
    "epochs": 40,
    "learning_rate": 1e-3,
    "validation_split": 0.2,
    "patience": 8
}

# Recommended top-5 crops for Kerala/South India
TARGET_CROPS = ["Rice", "Coconut", "Banana", "Pepper", "Rubber"]


def validate_dataset() -> list:
    data_dir = Path(CONFIG["data_dir"])
    if not data_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {data_dir}")

    classes = []
    total_images = 0
    for d in sorted([p for p in data_dir.iterdir() if p.is_dir()]):
        image_files = list(d.glob("*.jpg")) + list(d.glob("*.jpeg")) + list(d.glob("*.png"))
        if len(image_files) == 0:
            logger.warning(f"No images found in '{d.name}'")
            continue
        classes.append(d.name)
        total_images += len(image_files)
        logger.info(f"Class '{d.name}': {len(image_files)} images")

    if len(classes) < 2:
        raise ValueError("Need at least 2 classes with images to train crop model")

    # Warn if target crops are missing
    missing = [c for c in TARGET_CROPS if c not in classes]
    if missing:
        logger.warning(f"Missing recommended classes (optional): {missing}")

    logger.info(f"Dataset OK. Classes: {classes} | Total images: {total_images}")
    return classes


def create_generators():
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=25,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=CONFIG["validation_split"]
    )

    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=CONFIG["validation_split"]
    )

    train_gen = train_datagen.flow_from_directory(
        CONFIG["data_dir"],
        target_size=CONFIG["img_size"],
        batch_size=CONFIG["batch_size"],
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    val_gen = val_datagen.flow_from_directory(
        CONFIG["data_dir"],
        target_size=CONFIG["img_size"],
        batch_size=CONFIG["batch_size"],
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    return train_gen, val_gen


def build_model(num_classes: int) -> Model:
    try:
        base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(*CONFIG["img_size"], 3))
    except Exception as e:
        logger.warning(f"Failed to load ImageNet weights: {e}. Using random init.")
        base = MobileNetV2(weights=None, include_top=False, input_shape=(*CONFIG["img_size"], 3))

    base.trainable = False

    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    out = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base.input, outputs=out)
    model.compile(optimizer=Adam(learning_rate=CONFIG["learning_rate"]),
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def train(model: Model, train_gen, val_gen):
    model_dir = Path(CONFIG["model_dir"]) ; model_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = model_dir / "crop_model.h5"

    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=CONFIG["patience"], restore_best_weights=True, verbose=1),
        ModelCheckpoint(filepath=str(ckpt_path), monitor='val_accuracy', save_best_only=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6, verbose=1)
    ]

    hist = model.fit(
        train_gen,
        epochs=CONFIG["epochs"],
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )

    # Fine-tuning
    base_model = None
    for layer in model.layers:
        if hasattr(layer, 'layers') and len(layer.layers) > 0:
            base_model = layer
            break
    if base_model is not None:
        base_model.trainable = True
        fine_tune_at = len(base_model.layers) // 3
        for l in base_model.layers[:fine_tune_at]:
            l.trainable = False
        model.compile(optimizer=Adam(learning_rate=CONFIG["learning_rate"] / 10),
                      loss='categorical_crossentropy', metrics=['accuracy'])
        hist_fine = model.fit(
            train_gen,
            epochs=CONFIG["epochs"] // 2,
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )
    else:
        hist_fine = None

    return model, hist, hist_fine


def evaluate_and_save(model: Model, train_gen, val_gen, hist, hist_fine, label_map):
    model_dir = Path(CONFIG["model_dir"]) ; model_dir.mkdir(parents=True, exist_ok=True)

    # Save final model
    final_path = model_dir / "crop_model.h5"
    model.save(final_path)
    logger.info(f"Saved model: {final_path}")

    # Save label map
    with open(model_dir / "crop_label_map.json", "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    # Evaluate
    val_gen.reset()
    preds = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(preds, axis=1)
    y_true = val_gen.classes
    classes = list(val_gen.class_indices.keys())
    acc = float(np.mean(y_pred == y_true))

    report = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    with open(model_dir / "crop_training_summary.json", "w") as f:
        json.dump({
            "config": CONFIG,
            "accuracy": acc,
            "report": report,
            "num_classes": len(classes),
            "training_samples": train_gen.samples,
            "validation_samples": val_gen.samples
        }, f, indent=2)

    # Plots
    plt.figure(figsize=(15,5))
    plt.subplot(1,2,1)
    plt.plot(hist.history['accuracy'], label='train acc')
    plt.plot(hist.history['val_accuracy'], label='val acc')
    if hist_fine:
        plt.plot(hist_fine.history['accuracy'], label='ft train acc')
        plt.plot(hist_fine.history['val_accuracy'], label='ft val acc')
    plt.legend(); plt.title('Accuracy'); plt.xlabel('epoch'); plt.ylabel('acc')

    plt.subplot(1,2,2)
    plt.plot(hist.history['loss'], label='train loss')
    plt.plot(hist.history['val_loss'], label='val loss')
    if hist_fine:
        plt.plot(hist_fine.history['loss'], label='ft train loss')
        plt.plot(hist_fine.history['val_loss'], label='ft val loss')
    plt.legend(); plt.title('Loss'); plt.xlabel('epoch'); plt.ylabel('loss')
    plt.tight_layout()
    plt.savefig(model_dir / "crop_training_history.png", dpi=300, bbox_inches='tight')
    plt.close()

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted'); plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(model_dir / "crop_confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Validation accuracy: {acc:.4f}")


def main():
    logger.info("Starting crop type training…")
    classes = validate_dataset()
    train_gen, val_gen = create_generators()

    # Label map in multilingual keys (en only for crops; extend if needed)
    class_names = sorted(list(train_gen.class_indices.keys()), key=lambda c: train_gen.class_indices[c])
    label_map = {str(i): {"en": name} for i, name in enumerate(class_names)}

    model = build_model(num_classes=len(class_names))
    model.summary()
    model, hist, hist_fine = train(model, train_gen, val_gen)
    evaluate_and_save(model, train_gen, val_gen, hist, hist_fine, label_map)
    logger.info("Crop model training complete.")


if __name__ == "__main__":
    main()


