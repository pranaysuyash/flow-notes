#!/usr/bin/env python3
"""
Test script to verify the new learning mentor and quick notes functionality
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Test main note-taking system
        scripts_dir = project_root / "scripts"
        sys.path.insert(0, str(scripts_dir))
        
        from interactive_note_system import InteractiveNoteTakingSystem
        print("✓ InteractiveNoteTakingSystem imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import InteractiveNoteTakingSystem: {e}")
    
    try:
        # Test learning mentor
        from docs.learning_mentor import LearningMentorAgent
        print("✓ LearningMentorAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LearningMentorAgent: {e}")
    
    try:
        # Test quick notes
        from quick_notes import QuickNoteTakingSystem
        print("✓ QuickNoteTakingSystem imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QuickNoteTakingSystem: {e}")

def test_config():
    """Test that config is properly set up"""
    print("\nTesting configuration...")
    
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from config import OPENAI_MODEL, ANTHROPIC_MODEL, OLLAMA_MODEL, GOOGLE_MODEL, DEFAULT_LLM_PROVIDER
        print(f"✓ Config imported successfully")
        print(f"  OPENAI_MODEL: {OPENAI_MODEL}")
        print(f"  ANTHROPIC_MODEL: {ANTHROPIC_MODEL}")
        print(f"  OLLAMA_MODEL: {OLLAMA_MODEL}")
        print(f"  GOOGLE_MODEL: {GOOGLE_MODEL}")
        print(f"  DEFAULT_LLM_PROVIDER: {DEFAULT_LLM_PROVIDER}")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")

def test_directory_structure():
    """Test that expected directory structure exists"""
    print("\nTesting directory structure...")
    
    project_dir = Path.home() / "Projects" / "notes"
    expected_dirs = [
        project_dir / "topics",
        project_dir / "daily_notes",
        project_dir / "scripts",
        project_dir / "utils"
    ]
    
    for directory in expected_dirs:
        if directory.exists():
            print(f"✓ Directory exists: {directory}")
        else:
            print(f"⚠ Directory does not exist: {directory}")
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  Created directory: {directory}")

def main():
    print("Testing Learning Mentor System...")
    print("=" * 50)
    
    test_imports()
    test_config()
    test_directory_structure()
    
    print("\n" + "=" * 50)
    print("Testing completed. Check for any error messages above.")

if __name__ == "__main__":
    main()