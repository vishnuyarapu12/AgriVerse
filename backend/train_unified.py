#!/usr/bin/env python3
"""
Unified Training Script for AgriVerse

Train one of the following using a single CLI:
- rice: Rice leaf disease classifier (like train_model.py)
- banana: Banana leaf disease classifier (BananaLSD-style dataset)
- crops: Crop type classifier (like train_crop_model.py)

Usage examples:
  python backend/train_unified.py --task rice
  python backend/train_unified.py --task banana --data_dir datasets/banana_leaf_diseases
  python backend/train_unified.py --task crops --data_dir datasets/crops --epochs 60

Notes:
- This script does NOT modify existing training scripts. It provides an alternative, unified entry point.
- Outputs are saved under app/models with task-specific filenames.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Tuple

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
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_config(args: argparse.Namespace) -> Dict:
    default_dirs = {
        "rice": "datasets/rice_leaf_diseases",
        "banana": "datasets/banana_leaf_diseases",  # override with --data_dir if different
        "crops": "datasets/crops",
    }

    data_dir = args.data_dir or default_dirs.get(args.task, "datasets")
    model_dir = "app/models"

    return {
        "task": args.task,
        "data_dir": data_dir,
        "model_dir": model_dir,
        "img_size": (224, 224),
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "validation_split": args.validation_split,
        "patience": args.patience,
    }


def validate_dataset(data_dir: str) -> Tuple[bool, list, int]:
    p = Path(data_dir)
    if not p.exists():
        logger.error(f"Dataset directory not found: {p}")
        return False, [], 0

    classes = []
    total_images = 0
    for d in sorted([x for x in p.iterdir() if x.is_dir()]):
        imgs = []
        imgs += list(d.glob("*.jpg"))
        imgs += list(d.glob("*.jpeg"))
        imgs += list(d.glob("*.png"))
        if len(imgs) == 0:
            logger.warning(f"No images found in '{d.name}'")
            continue
        classes.append(d.name)
        total_images += len(imgs)
        logger.info(f"Class '{d.name}': {len(imgs)} images")

    ok = len(classes) >= 2
    if not ok:
        logger.error("Need at least 2 classes with images to train")
    else:
        logger.info(f"Dataset OK. Classes: {classes} | Total images: {total_images}")
    return ok, classes, total_images


def create_generators(config: Dict):
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=25,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=config["validation_split"]
    )

    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=config["validation_split"]
    )

    train_gen = train_datagen.flow_from_directory(
        config["data_dir"],
        target_size=config["img_size"],
        batch_size=config["batch_size"],
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    val_gen = val_datagen.flow_from_directory(
        config["data_dir"],
        target_size=config["img_size"],
        batch_size=config["batch_size"],
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    return train_gen, val_gen


def build_model(config: Dict, num_classes: int) -> Model:
    try:
        base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(*config["img_size"], 3))
    except Exception as e:
        logger.warning(f"Failed to load ImageNet weights: {e}. Using random init.")
        base = MobileNetV2(weights=None, include_top=False, input_shape=(*config["img_size"], 3))

    base.trainable = False

    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    out = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base.input, outputs=out)
    model.compile(optimizer=Adam(learning_rate=config["learning_rate"]),
                  loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def train(model: Model, config: Dict, train_gen, val_gen):
    model_dir = Path(config["model_dir"]) ; model_dir.mkdir(parents=True, exist_ok=True)
    ckpt_name = {
        "rice": "rice_disease_model.h5",
        "banana": "banana_disease_model.h5",
        "crops": "crop_model.h5",
    }.get(config["task"], "model.h5")

    ckpt_path = model_dir / ckpt_name

    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=config["patience"], restore_best_weights=True, verbose=1),
        ModelCheckpoint(filepath=str(ckpt_path), monitor='val_accuracy', save_best_only=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6, verbose=1)
    ]

    hist = model.fit(
        train_gen,
        epochs=config["epochs"],
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
        model.compile(optimizer=Adam(learning_rate=config["learning_rate"] / 10),
                      loss='categorical_crossentropy', metrics=['accuracy'])
        hist_fine = model.fit(
            train_gen,
            epochs=max(1, config["epochs"] // 2),
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )
    else:
        hist_fine = None

    return model, hist, hist_fine


def evaluate_and_save(model: Model, config: Dict, train_gen, val_gen, hist, hist_fine, label_map):
    model_dir = Path(config["model_dir"]) ; model_dir.mkdir(parents=True, exist_ok=True)

    # Save final model
    final_name = {
        "rice": "rice_disease_model.h5",
        "banana": "banana_disease_model.h5",
        "crops": "crop_model.h5",
    }.get(config["task"], "model.h5")
    final_path = model_dir / final_name
    model.save(final_path)
    logger.info(f"Saved model: {final_path}")

    # Save label map
    label_name = {
        "rice": "label_map.json",
        "banana": "banana_label_map.json",
        "crops": "crop_label_map.json",
    }.get(config["task"], "label_map.json")
    with open(model_dir / label_name, "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    # Evaluate
    val_gen.reset()
    preds = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(preds, axis=1)
    y_true = val_gen.classes
    classes = list(val_gen.class_indices.keys())
    acc = float(np.mean(y_pred == y_true))

    report = classification_report(y_true, y_pred, target_names=classes, output_dict=True)

    summary_name = {
        "rice": "training_summary.json",
        "banana": "banana_training_summary.json",
        "crops": "crop_training_summary.json",
    }.get(config["task"], "training_summary.json")

    with open(model_dir / summary_name, "w") as f:
        json.dump({
            "config": config,
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

    hist_name = {
        "rice": "training_history.png",
        "banana": "banana_training_history.png",
        "crops": "crop_training_history.png",
    }.get(config["task"], "training_history.png")
    plt.savefig(Path(config["model_dir"]) / hist_name, dpi=300, bbox_inches='tight')
    plt.close()

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted'); plt.ylabel('Actual')
    plt.tight_layout()

    cm_name = {
        "rice": "confusion_matrix.png",
        "banana": "banana_confusion_matrix.png",
        "crops": "crop_confusion_matrix.png",
    }.get(config["task"], "confusion_matrix.png")
    plt.savefig(Path(config["model_dir"]) / cm_name, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Validation accuracy: {acc:.4f}")


def main():
    parser = argparse.ArgumentParser(description="Unified trainer for AgriVerse models")
    parser.add_argument("--task", choices=["rice", "banana", "crops"], required=True,
                        help="What to train: rice (diseases), banana (diseases), crops (crop types)")
    parser.add_argument("--data_dir", type=str, default=None,
                        help="Path to dataset root (folder with class subfolders)")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--learning_rate", type=float, default=1e-3)
    parser.add_argument("--validation_split", type=float, default=0.2)
    parser.add_argument("--patience", type=int, default=8)

    args = parser.parse_args()
    config = build_config(args)

    logger.info("Starting unified training…")
    logger.info(json.dumps({k: v for k, v in config.items() if k != 'learning_rate'}, indent=2))

    ok, classes, _ = validate_dataset(config["data_dir"])
    if not ok:
        sys.exit(1)

    train_gen, val_gen = create_generators(config)

    # Label map (English only; extend if needed)
    class_names = sorted(list(train_gen.class_indices.keys()), key=lambda c: train_gen.class_indices[c])
    label_map = {str(i): {"en": name} for i, name in enumerate(class_names)}

    model = build_model(config, num_classes=len(class_names))
    model.summary()
    model, hist, hist_fine = train(model, config, train_gen, val_gen)
    evaluate_and_save(model, config, train_gen, val_gen, hist, hist_fine, label_map)
    logger.info("Unified training complete.")


if __name__ == "__main__":
    main()


