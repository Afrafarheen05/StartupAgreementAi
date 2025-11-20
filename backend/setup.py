"""
Setup Script
Initialize the backend environment
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"✅ {description} - Complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e}")
        return False


def main():
    """Setup backend environment"""
    print("\n" + "="*60)
    print("AgreemShield AI - Backend Setup")
    print("="*60)
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    
    if sys.version_info < (3, 9):
        print("\n⚠️  Warning: Python 3.9+ recommended")
    
    # Install Python dependencies
    print("\n" + "="*60)
    print("Step 1: Installing Python dependencies")
    print("="*60)
    
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        print(f"\n❌ Error: requirements.txt not found at {requirements_path}")
        return
    
    print("\nThis will install:")
    print("  • FastAPI & Uvicorn (Web framework)")
    print("  • scikit-learn (Machine Learning)")
    print("  • spaCy (NLP)")
    print("  • transformers & torch (Deep Learning)")
    print("  • PyPDF2, python-docx (Document processing)")
    print("  • And more...")
    
    if not run_command(
        f'pip install -r "{requirements_path}"',
        "Installing Python packages"
    ):
        print("\n⚠️  Some packages may have failed to install")
        print("You may need to install them manually")
    
    # Download spaCy model
    print("\n" + "="*60)
    print("Step 2: Downloading spaCy language model")
    print("="*60)
    
    run_command(
        "python -m spacy download en_core_web_sm",
        "Downloading spaCy English model"
    )
    
    # Create necessary directories
    print("\n" + "="*60)
    print("Step 3: Creating directories")
    print("="*60)
    
    backend_dir = os.path.dirname(__file__)
    dirs_to_create = [
        os.path.join(backend_dir, 'uploads'),
        os.path.join(backend_dir, 'trained_models')
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created: {dir_path}")
    
    # Check for training data
    print("\n" + "="*60)
    print("Step 4: Checking training data")
    print("="*60)
    
    csv_path = os.path.join(os.path.dirname(backend_dir), 'labeled_clauses.csv')
    
    if os.path.exists(csv_path):
        print(f"✅ Found training data: {csv_path}")
        
        # Count lines
        with open(csv_path, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f) - 1  # Subtract header
        
        print(f"   Training samples: {line_count}")
    else:
        print(f"⚠️  Training data not found: {csv_path}")
        print("   You'll need labeled_clauses.csv to train the model")
    
    # Summary
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("\n1. Train the model:")
    print("   python backend/train_model.py")
    
    print("\n2. Start the backend server:")
    print("   cd backend")
    print("   python -m app.main")
    print("   OR")
    print("   uvicorn app.main:app --reload")
    
    print("\n3. Start the frontend (in separate terminal):")
    print("   npm run dev")
    
    print("\n4. Open browser:")
    print("   http://localhost:5173")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
