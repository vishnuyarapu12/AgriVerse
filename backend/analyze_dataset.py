#!/usr/bin/env python3
"""
Dataset Quality & Analysis Tool
- Analyze dataset structure
- Detect class imbalance
- Check image quality
- Suggest optimization strategies
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_to_serializable(obj):
    """Convert NumPy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    return obj


def analyze_dataset(data_dir: str) -> Dict:
    """Analyze dataset and return statistics"""
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.error(f"Dataset not found: {data_dir}")
        return {}
    
    stats = {
        'total_images': 0,
        'classes': {},
        'image_sizes': [],
        'corrupted_files': [],
        'class_imbalance': None,
        'recommendations': []
    }
    
    logger.info(f"\n📊 Analyzing dataset: {data_dir}\n")
    
    # Scan all classes
    for class_dir in sorted(data_path.iterdir()):
        if not class_dir.is_dir():
            continue
        
        class_name = class_dir.name
        image_count = 0
        image_sizes = []
        
        # Count images and check quality
        image_files = (
            list(class_dir.glob("*.jpg")) +
            list(class_dir.glob("*.jpeg")) +
            list(class_dir.glob("*.png")) +
            list(class_dir.glob("*.JPG")) +
            list(class_dir.glob("*.PNG"))
        )
        
        for img_file in image_files:
            try:
                with Image.open(img_file) as img:
                    # Check if valid image
                    img.verify()
                    
                    # Reopen to get size (verify closes the file)
                    with Image.open(img_file) as img2:
                        image_sizes.append(img2.size)
                        image_count += 1
                        
            except Exception as e:
                stats['corrupted_files'].append(str(img_file))
                logger.warning(f"⚠️  Corrupted: {img_file.name} - {type(e).__name__}")
        
        if image_count > 0:
            avg_size = tuple(int(x) for x in np.mean(image_sizes, axis=0)) if image_sizes else None
            min_size = tuple(int(x) for x in np.min(image_sizes, axis=0)) if image_sizes else None
            max_size = tuple(int(x) for x in np.max(image_sizes, axis=0)) if image_sizes else None
            
            stats['classes'][class_name] = {
                'count': image_count,
                'avg_size': avg_size,
                'min_size': min_size,
                'max_size': max_size,
            }
            stats['total_images'] += image_count
            stats['image_sizes'].extend(image_sizes)
            
            logger.info(f"✓ {class_name:30} | {image_count:4} images | "
                       f"Size: {stats['classes'][class_name]['min_size']} → "
                       f"{stats['classes'][class_name]['max_size']}")
    
    # Calculate class imbalance
    if stats['classes']:
        counts = [c['count'] for c in stats['classes'].values()]
        min_count = min(counts)
        max_count = max(counts)
        imbalance_ratio = max_count / min_count if min_count > 0 else 0
        
        stats['class_imbalance'] = {
            'ratio': imbalance_ratio,
            'min_class_count': min_count,
            'max_class_count': max_count,
            'num_classes': len(stats['classes'])
        }
    
    # Generate recommendations
    stats['recommendations'] = get_recommendations(stats)
    
    # Print summary
    print_summary(stats)
    
    return stats


def get_recommendations(stats: Dict) -> List[str]:
    """Generate recommendations based on dataset analysis"""
    
    recommendations = []
    
    if not stats['classes']:
        recommendations.append("❌ No valid images found!")
        return recommendations
    
    # Check total images
    total = stats['total_images']
    if total < 300:
        recommendations.append(f"⚠️  Only {total} total images - may cause overfitting. Target: 500+")
    elif total < 1000:
        recommendations.append(f"✓ {total} images is decent. Aim for 1000+ for best results")
    elif total >= 2000:
        recommendations.append(f"✅ Excellent! {total} images should give very high accuracy")
    
    # Check per-class samples
    avg_per_class = total / len(stats['classes']) if stats['classes'] else 0
    if avg_per_class < 100:
        recommendations.append(f"⚠️  Only ~{int(avg_per_class)} images per class. Minimum 100-200 recommended")
    elif avg_per_class < 300:
        recommendations.append(f"✓ ~{int(avg_per_class)} images per class is okay")
    else:
        recommendations.append(f"✅ ~{int(avg_per_class)} images per class - excellent!")
    
    # Check class balance
    if stats['class_imbalance']:
        ratio = stats['class_imbalance']['ratio']
        if ratio > 3:
            recommendations.append(f"⚠️  Class imbalance detected (ratio: {ratio:.1f}x). "
                                 "Consider using class weights or augmentation")
        elif ratio > 1.5:
            recommendations.append(f"✓ Slight class imbalance ({ratio:.1f}x) - manageable")
        else:
            recommendations.append(f"✅ Good class balance ({ratio:.1f}x)")
    
    # Check image sizes
    if stats['image_sizes']:
        sizes = np.array(stats['image_sizes'])
        avg_size = np.mean(sizes, axis=0)
        if np.std(sizes, axis=0).max() > 100:
            recommendations.append(f"⚠️  High variation in image sizes. Training script handles this")
        recommendations.append(f"📏 Average image size: {int(avg_size[0])}×{int(avg_size[1])}")
    
    # Check corrupted files
    if stats['corrupted_files']:
        recommendations.append(f"⚠️  {len(stats['corrupted_files'])} corrupted files found - removing them")
    
    return recommendations


def print_summary(stats: Dict):
    """Print formatted summary"""
    
    print("\n" + "="*70)
    print("DATASET ANALYSIS SUMMARY")
    print("="*70)
    
    if not stats['classes']:
        print("❌ No valid dataset found")
        return
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Images: {stats['total_images']}")
    print(f"   Total Classes: {len(stats['classes'])}")
    
    if stats['class_imbalance']:
        print(f"   Class Imbalance: {stats['class_imbalance']['ratio']:.2f}x")
        print(f"     Min/Max: {stats['class_imbalance']['min_class_count']} / "
              f"{stats['class_imbalance']['max_class_count']}")
    
    print(f"\n📋 Per-Class Breakdown:")
    for class_name, info in sorted(stats['classes'].items(), 
                                   key=lambda x: x[1]['count'], reverse=True):
        print(f"   {class_name:30} {info['count']:4} images")
    
    if stats['corrupted_files']:
        print(f"\n⚠️  {len(stats['corrupted_files'])} Corrupted Files:")
        for f in stats['corrupted_files'][:5]:
            print(f"   - {f}")
        if len(stats['corrupted_files']) > 5:
            print(f"   ... and {len(stats['corrupted_files']) - 5} more")
    
    print(f"\n💡 Recommendations for High Accuracy:")
    for rec in stats['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "="*70 + "\n")


def remove_corrupted(data_dir: str):
    """Remove corrupted image files"""
    
    data_path = Path(data_dir)
    removed = 0
    
    logger.info(f"🧹 Scanning for corrupted files in {data_dir}...\n")
    
    for class_dir in data_path.iterdir():
        if not class_dir.is_dir():
            continue
        
        for img_file in (
            list(class_dir.glob("*.jpg")) +
            list(class_dir.glob("*.jpeg")) +
            list(class_dir.glob("*.png")) +
            list(class_dir.glob("*.JPG")) +
            list(class_dir.glob("*.PNG"))
        ):
            try:
                with Image.open(img_file) as img:
                    img.verify()
            except Exception as e:
                logger.warning(f"Removing corrupted: {img_file.name}")
                img_file.unlink()
                removed += 1
    
    logger.info(f"\n✅ Removed {removed} corrupted files")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze and clean dataset")
    parser.add_argument("--data_dir", default="archive/dataset", help="Dataset directory")
    parser.add_argument("--clean", action="store_true", help="Remove corrupted files")
    
    args = parser.parse_args()
    
    # Analyze dataset
    stats = analyze_dataset(args.data_dir)
    
    # Clean if requested
    if args.clean and stats.get('corrupted_files'):
        logger.info(f"\nRemoving {len(stats['corrupted_files'])} corrupted files...")
        remove_corrupted(args.data_dir)
    
    # Save report
    report_path = Path(args.data_dir) / "dataset_analysis.json"
    with open(report_path, 'w') as f:
        # Convert for JSON serialization
        report = {
            'total_images': stats['total_images'],
            'classes': {
                k: {
                    'count': v['count'],
                    'avg_size': v['avg_size'],
                    'min_size': v['min_size'],
                    'max_size': v['max_size'],
                }
                for k, v in stats['classes'].items()
            },
            'class_imbalance': stats['class_imbalance'],
            'corrupted_files': len(stats['corrupted_files']),
            'recommendations': stats['recommendations']
        }
        # Convert all NumPy types to Python native types
        report = convert_to_serializable(report)
        json.dump(report, f, indent=2)
    
    logger.info(f"📄 Report saved: {report_path}")


if __name__ == "__main__":
    main()
