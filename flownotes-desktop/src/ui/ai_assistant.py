"""
AI Assistant Panel for FlowNotes Desktop
Floating/dockable panel with one-click AI enhancements
"""

import sys
from pathlib import Path

# Add parent dirs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QTextEdit, QLabel, QScrollArea, QFrame, QProgressBar
    )
    from PySide6.QtCore import Qt, Signal, QThread
    from PySide6.QtGui import QFont
except ImportError:
    print("PySide6 not installed")
    raise


class AIWorker(QThread):
    """Background worker for AI processing"""

    finished = Signal(str, str)  # enhancement_type, result
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, enhancement_type: str, content: str, llm_service):
        super().__init__()
        self.enhancement_type = enhancement_type
        self.content = content
        self.llm_service = llm_service

    def run(self):
        """Run AI enhancement in background"""
        try:
            self.progress.emit(25)

            # Call LLM service (placeholder - will integrate actual service)
            result = self._generate_enhancement()

            self.progress.emit(100)
            self.finished.emit(self.enhancement_type, result)

        except Exception as e:
            self.error.emit(str(e))

    def _generate_enhancement(self) -> str:
        """Generate AI enhancement (placeholder)"""
        # TODO: Integrate with actual LLM service from utils/async_llm.py
        import time
        time.sleep(1)  # Simulate API call

        templates = {
            "summary": f"📋 **TL;DR Summary**\n\n• Key point 1 from your notes\n• Key point 2\n• Key point 3",
            "tags": f"🏷️ **Key Concepts**\n\n#concept1 #concept2 #concept3 #concept4 #concept5",
            "diagram": f"```mermaid\ngraph TD\n    A[Main Concept] --> B[Sub-concept 1]\n    A --> C[Sub-concept 2]\n```",
            "quiz": f"❓ **Review Questions**\n\n1. What is the main concept?\n2. How does X relate to Y?\n3. When would you use this?",
            "flashcards": f"🗂️ **Flashcards Generated**\n\n✓ 8 cards created\n✓ Ready for review",
            "insights": f"💡 **Learning Insights**\n\nThis topic connects to:\n- Related Concept A\n- Related Concept B\n\nNext steps: Practice with examples",
        }

        return templates.get(self.enhancement_type, "Enhancement generated!")


class AIAssistantPanel(QWidget):
    """AI Assistant panel widget"""

    enhancement_generated = Signal(str, str)  # type, content

    def __init__(self):
        super().__init__()

        self.current_worker = None
        self.current_note_content = ""

        self.setup_ui()

    def setup_ui(self):
        """Setup AI assistant UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("🤖 AI Assistant")
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #7C3AED;
            padding: 8px;
        """)
        layout.addWidget(header)

        # Suggestions section
        suggestions_label = QLabel("💡 Quick Actions")
        suggestions_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(suggestions_label)

        # Enhancement buttons
        self.create_enhancement_buttons(layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3A3A4F;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #7C3AED;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Results area
        results_label = QLabel("📝 Results")
        results_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 12px;")
        layout.addWidget(results_label)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setPlaceholderText("AI-generated content will appear here...")
        self.results_area.setMaximumHeight(200)
        layout.addWidget(self.results_area)

        # Insert button
        self.insert_button = QPushButton("Insert into Note")
        self.insert_button.setEnabled(False)
        self.insert_button.clicked.connect(self.on_insert_clicked)
        layout.addWidget(self.insert_button)

        # Spacer
        layout.addStretch()

        # Tips section
        tips_frame = QFrame()
        tips_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D3F;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        tips_layout = QVBoxLayout(tips_frame)

        tips_label = QLabel("💡 <b>Tip:</b> Select text before enhancing for better results!")
        tips_label.setWordWrap(True)
        tips_label.setStyleSheet("font-size: 12px; color: #A0A0AB;")
        tips_layout.addWidget(tips_label)

        layout.addWidget(tips_frame)

    def create_enhancement_buttons(self, layout: QVBoxLayout):
        """Create enhancement action buttons"""
        enhancements = [
            ("📋 Summary", "summary", "Generate TL;DR summary"),
            ("🏷️ Tags", "tags", "Extract key concepts"),
            ("📊 Diagram", "diagram", "Create visual concept map"),
            ("❓ Quiz", "quiz", "Generate review questions"),
            ("🗂️ Flashcards", "flashcards", "Create study cards"),
            ("💡 Insights", "insights", "Get learning insights"),
        ]

        # Create 2-column grid
        for i in range(0, len(enhancements), 2):
            row_layout = QHBoxLayout()

            for j in range(2):
                if i + j < len(enhancements):
                    label, enhancement_type, tooltip = enhancements[i + j]

                    btn = QPushButton(label)
                    btn.setToolTip(tooltip)
                    btn.setMinimumHeight(40)
                    btn.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding-left: 12px;
                            font-size: 13px;
                        }
                    """)
                    btn.clicked.connect(
                        lambda checked, t=enhancement_type: self.generate_enhancement(t)
                    )

                    row_layout.addWidget(btn)

            layout.addLayout(row_layout)

    def set_note_content(self, content: str):
        """Update current note content"""
        self.current_note_content = content

    def generate_enhancement(self, enhancement_type: str):
        """Generate AI enhancement"""
        if not self.current_note_content.strip():
            self.results_area.setPlainText("⚠️ Please write some notes first!")
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_area.setPlainText(f"Generating {enhancement_type}...")

        # Disable buttons during processing
        self.setEnabled(False)

        # Start worker thread
        self.current_worker = AIWorker(
            enhancement_type,
            self.current_note_content,
            None  # TODO: Pass actual LLM service
        )

        self.current_worker.finished.connect(self.on_enhancement_finished)
        self.current_worker.error.connect(self.on_enhancement_error)
        self.current_worker.progress.connect(self.progress_bar.setValue)

        self.current_worker.start()

    def on_enhancement_finished(self, enhancement_type: str, result: str):
        """Handle enhancement completion"""
        self.results_area.setPlainText(result)
        self.insert_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.setEnabled(True)

        # Emit signal for main window
        self.enhancement_generated.emit(enhancement_type, result)

    def on_enhancement_error(self, error: str):
        """Handle enhancement error"""
        self.results_area.setPlainText(f"❌ Error: {error}")
        self.progress_bar.setVisible(False)
        self.setEnabled(True)

    def on_insert_clicked(self):
        """Insert result into note"""
        # This will be handled by main window
        result = self.results_area.toPlainText()
        self.enhancement_generated.emit("insert", result)


# Standalone test
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test window
    window = AIAssistantPanel()
    window.setWindowTitle("AI Assistant Panel")
    window.resize(350, 600)
    window.show()

    # Set test content
    window.set_note_content("""
# Neural Networks

Neural networks are computing systems inspired by biological neural networks.

## Key Components
- Input layer
- Hidden layers
- Output layer
- Weights and biases
- Activation functions

Backpropagation is used to train the network.
    """)

    sys.exit(app.exec())
