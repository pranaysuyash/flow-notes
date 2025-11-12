#!/usr/bin/env python3
"""
Test script to verify the topic-based organization of notes
"""
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_topic_organization():
    """Test that the note-taking system organizes by topic first, then by date"""
    project_dir = Path.home() / "Projects" / "notes"
    topics_dir = project_dir / "topics"
    
    print("Testing topic-based organization...")
    print(f"Project directory: {project_dir}")
    print(f"Topics directory: {topics_dir}")
    
    if topics_dir.exists():
        print("\nExisting topics:")
        for topic_dir in topics_dir.iterdir():
            if topic_dir.is_dir():
                print(f"  - {topic_dir.name}")
                for note_file in topic_dir.iterdir():
                    print(f"    - {note_file.name}")
    else:
        print(f"\nTopics directory does not exist yet. It will be created when you run the note-taking system.")
        print(f"Directory should be created at: {topics_dir}")
    
    print("\nExpected structure after running the interactive note system:")
    print("  ~/Projects/notes/topics/<topic-name>/<date>.md")
    print("  ~/Projects/notes/topics/<topic-name>/comments_<date>.md")
    print("  ~/Projects/notes/topics/<topic-name>/consolidated_guide_<date>.md")

if __name__ == "__main__":
    test_topic_organization()