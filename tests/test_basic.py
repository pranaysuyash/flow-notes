"""
Basic tests for the note-taking system
Run with: python -m pytest tests/ or python tests/test_basic.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_operations import sanitize_topic_name, ensure_directory_exists
from utils.learning_enhancements import LearningEnhancer
from utils.researcher_mode import ResearchAssistant


def test_sanitize_topic_name():
    """Test topic name sanitization"""
    try:
        result = sanitize_topic_name("Machine Learning")
        assert result == "machine-learning", f"Expected 'machine-learning', got '{result}'"
        
        result = sanitize_topic_name("Web Dev!")
        assert result == "web-dev", f"Expected 'web-dev', got '{result}'"
        
        result = sanitize_topic_name("C++  Programming")
        # The function keeps alphanumeric, spaces, and hyphens, so ++ becomes --
        assert result == "c--programming", f"Expected 'c--programming', got '{result}'"
        
        result = sanitize_topic_name("Data Science 101")
        assert result == "data-science-101", f"Expected 'data-science-101', got '{result}'"

        long_input = "using opencv-contrib-python reading images using imread while for videos need to use videocapture and frame by frame reading"
        result = sanitize_topic_name(long_input)
        assert len(result) <= 80, "Expected long topic names to be truncated for filesystem safety"
        assert result.startswith("using-opencv-contrib-python"), "Expected truncation to preserve readable prefix"
        
        print("✅ Topic sanitization tests passed")
    except Exception as e:
        print(f"❌ Topic sanitization failed: {e}")
        raise


def test_ensure_directory():
    """Test directory creation"""
    test_dir = Path("/tmp/test_notes_dir")
    result = ensure_directory_exists(test_dir)
    assert result.exists()
    assert result.is_dir()
    
    # Clean up
    result.rmdir()
    print("✅ Directory creation tests passed")


def test_learning_enhancer_init():
    """Test LearningEnhancer initialization"""
    def mock_llm(messages, temperature=0.7):
        return "Mock response"
    
    enhancer = LearningEnhancer(mock_llm, "Test agent prompt")
    assert enhancer.call_llm is not None
    assert enhancer.agent_prompt == "Test agent prompt"
    print("✅ LearningEnhancer initialization tests passed")


def test_researcher_init():
    """Test ResearchAssistant initialization"""
    def mock_llm(messages, temperature=0.7):
        return "Mock response"
    
    researcher = ResearchAssistant(mock_llm, "Test agent prompt")
    assert researcher.call_llm is not None
    assert researcher.agent_prompt == "Test agent prompt"
    print("✅ ResearchAssistant initialization tests passed")


def test_auto_tags_empty_content():
    """Test auto-tagging with empty content"""
    def mock_llm(messages, temperature=0.7):
        return "tag1, tag2, tag3"
    
    enhancer = LearningEnhancer(mock_llm, "Test prompt")
    
    # Empty content should return empty list
    result = enhancer.generate_auto_tags("")
    assert result == []
    
    # With content should call LLM
    result = enhancer.generate_auto_tags("Some test content")
    assert len(result) == 3
    print("✅ Auto-tagging tests passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("Running Note-Taking System Tests")
    print("="*50 + "\n")
    
    try:
        test_sanitize_topic_name()
        test_ensure_directory()
        test_learning_enhancer_init()
        test_researcher_init()
        test_auto_tags_empty_content()
        
        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50 + "\n")
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
