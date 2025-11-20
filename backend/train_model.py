"""
Model Training Script
Train the risk classification model from labeled data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml.risk_classifier import RiskClassifier


def main():
    """Train model from labeled_clauses.csv"""
    print("="*60)
    print("AgreemShield AI - Model Training")
    print("="*60)
    
    # Path to training data
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'labeled_clauses.csv')
    
    if not os.path.exists(csv_path):
        print(f"\n❌ Error: Training data not found at {csv_path}")
        print("\nPlease ensure labeled_clauses.csv is in the project root directory.")
        return
    
    print(f"\n📂 Training data: {csv_path}")
    
    # Initialize classifier
    print("\n🔧 Initializing classifier...")
    classifier = RiskClassifier()
    
    # Train model
    print("\n🚀 Training model...")
    print("-" * 60)
    
    result = classifier.train_from_csv(csv_path)
    
    print("\n" + "="*60)
    if result['success']:
        print("✅ Training completed successfully!")
        print("="*60)
        
        metrics = result.get('metrics', {})
        print(f"\n📊 Model Performance:")
        print(f"   Accuracy: {metrics.get('accuracy', 0)*100:.1f}%")
        print(f"   Training samples: {metrics.get('training_samples', 0)}")
        
        print(f"\n💾 Model saved to: {result.get('model_path')}")
        
        print("\n✅ Model is ready for use!")
        print("\nYou can now:")
        print("  1. Start the backend server: python -m backend.app.main")
        print("  2. Upload documents for analysis")
        print("  3. Get real-time risk predictions")
        
    else:
        print("❌ Training failed!")
        print("="*60)
        print(f"\nError: {result.get('error')}")
        return
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
