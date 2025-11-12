#!/bin/bash
# Enhanced wrapper script to start the note-taking system with learning mentor capabilities

cd "$(dirname "$0")"

echo "Learning Mentor Note-Taking System"
echo "Choose an option:"
echo "1) Interactive Note-Taking System (full features)"
echo "2) Quick Notes with Learning Mentor"
echo "3) Learning Mentor Only"
echo -n "Enter your choice (1-3) [default: 1]: "
read choice

case $choice in
    2)
        echo "Starting Quick Notes with Learning Mentor..."
        python3 quick_notes.py
        ;;
    3)
        echo "Starting Learning Mentor Only..."
        python3 learning_mentor.py
        ;;
    1|"")
        echo "Starting Interactive Note-Taking System..."
        python3 scripts/interactive_note_system.py
        ;;
    *)
        echo "Invalid choice. Defaulting to Interactive Note-Taking System..."
        python3 scripts/interactive_note_system.py
        ;;
esac