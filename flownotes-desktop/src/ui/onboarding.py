"""
Interactive Onboarding Tutorial for FlowNotes Desktop
Guides new users through first-time setup and key features
"""

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
        QLabel, QWidget, QStackedWidget
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QPixmap
except ImportError:
    print("PySide6 not installed")
    raise


class OnboardingDialog(QDialog):
    """Onboarding tutorial dialog"""

    finished = Signal(bool)  # completed or skipped

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_step = 0
        self.total_steps = 5

        self.setup_ui()
        self.setWindowTitle("Welcome to FlowNotes!")
        self.resize(600, 450)

        # Modal dialog
        self.setModal(True)

    def setup_ui(self):
        """Setup onboarding UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Steps container
        self.steps_widget = QStackedWidget()

        # Create all steps
        self.steps_widget.addWidget(self.create_welcome_step())
        self.steps_widget.addWidget(self.create_editor_step())
        self.steps_widget.addWidget(self.create_ai_step())
        self.steps_widget.addWidget(self.create_shortcuts_step())
        self.steps_widget.addWidget(self.create_complete_step())

        layout.addWidget(self.steps_widget)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        self.skip_button = QPushButton("Skip Tutorial")
        self.skip_button.clicked.connect(lambda: self.finish_onboarding(False))

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.previous_step)
        self.back_button.setEnabled(False)

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self.next_step)

        nav_layout.addWidget(self.skip_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

        # Progress indicator
        self.progress_label = QLabel(f"Step 1 of {self.total_steps}")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #A0A0AB; font-size: 12px;")
        layout.addWidget(self.progress_label)

    def create_welcome_step(self) -> QWidget:
        """Create welcome step"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Title
        title = QLabel("Welcome to FlowNotes! 🎉")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #7C3AED;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Transform your notes into comprehensive learning materials")
        subtitle.setStyleSheet("font-size: 16px; color: #A0A0AB;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Features list
        features = QLabel("""
<div style='line-height: 1.8; font-size: 14px;'>
<p><b style='color: #7C3AED;'>✨ What you'll learn:</b></p>
<ul style='margin-left: 20px;'>
    <li>Create and organize your notes</li>
    <li>Use AI to generate flashcards and quizzes</li>
    <li>Master keyboard shortcuts for faster workflow</li>
    <li>Review and study with spaced repetition</li>
</ul>
</div>
        """)
        features.setWordWrap(True)
        features.setTextFormat(Qt.RichText)
        layout.addWidget(features)

        # Time estimate
        time_label = QLabel("⏱️ Takes about 2 minutes")
        time_label.setStyleSheet("color: #10B981; font-size: 13px; font-weight: bold;")
        time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_label)

        layout.addStretch()

        return widget

    def create_editor_step(self) -> QWidget:
        """Create editor introduction step"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Title
        title = QLabel("📝 The Editor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #7C3AED;")
        layout.addWidget(title)

        # Description
        desc = QLabel("""
<div style='font-size: 14px; line-height: 1.6;'>
<p>FlowNotes uses <b>Markdown</b> for formatting. Don't worry, it's super simple!</p>

<p><b style='color: #7C3AED;'>Quick Markdown Guide:</b></p>
<ul style='margin-left: 20px;'>
    <li><code># Heading</code> - Create headings</li>
    <li><code>**bold**</code> - Make text bold</li>
    <li><code>*italic*</code> - Make text italic</li>
    <li><code>- item</code> - Create lists</li>
    <li><code>`code`</code> - Inline code</li>
    <li><code>[link](url)</code> - Add links</li>
</ul>

<p><b style='color: #10B981;'>Live Preview:</b> See your formatted notes in real-time on the right!</p>
</div>
        """)
        desc.setWordWrap(True)
        desc.setTextFormat(Qt.RichText)
        layout.addWidget(desc)

        # Example
        example_box = QWidget()
        example_box.setStyleSheet("""
            background-color: #2D2D3F;
            border-radius: 6px;
            padding: 16px;
        """)
        example_layout = QVBoxLayout(example_box)

        example_title = QLabel("<b>Try This:</b>")
        example_title.setStyleSheet("color: #EC4899; font-size: 13px;")
        example_layout.addWidget(example_title)

        example_text = QLabel("""
# My First Note

This is **really important**!

- Point 1
- Point 2
        """)
        example_text.setStyleSheet("font-family: 'Courier New'; font-size: 12px; color: #E0E0E6;")
        example_layout.addWidget(example_text)

        layout.addWidget(example_box)
        layout.addStretch()

        return widget

    def create_ai_step(self) -> QWidget:
        """Create AI features step"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Title
        title = QLabel("✨ AI Magic")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #7C3AED;")
        layout.addWidget(title)

        # Description
        desc = QLabel("""
<div style='font-size: 14px; line-height: 1.6;'>
<p>This is where FlowNotes shines! Our AI can automatically generate:</p>
</div>
        """)
        desc.setWordWrap(True)
        desc.setTextFormat(Qt.RichText)
        layout.addWidget(desc)

        # Features grid
        features_layout = QVBoxLayout()
        features = [
            ("📋", "TL;DR Summaries", "3-5 bullet point overview"),
            ("🏷️", "Smart Tags", "Key concepts extracted automatically"),
            ("📊", "Visual Diagrams", "Concept maps and flowcharts"),
            ("❓", "Quiz Questions", "Test your understanding"),
            ("🗂️", "Flashcards", "Ready for spaced repetition"),
            ("💡", "Learning Insights", "Next steps and connections"),
        ]

        for emoji, name, description in features:
            feature_widget = QWidget()
            feature_layout = QHBoxLayout(feature_widget)
            feature_layout.setContentsMargins(0, 4, 0, 4)

            emoji_label = QLabel(emoji)
            emoji_label.setStyleSheet("font-size: 20px;")
            feature_layout.addWidget(emoji_label)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(0)

            name_label = QLabel(f"<b>{name}</b>")
            name_label.setStyleSheet("font-size: 13px; color: #E0E0E6;")
            text_layout.addWidget(name_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 11px; color: #A0A0AB;")
            text_layout.addWidget(desc_label)

            feature_layout.addLayout(text_layout)
            features_layout.addWidget(feature_widget)

        layout.addLayout(features_layout)

        # CTA
        cta = QLabel("🚀 <b>Just click a button in the AI panel and watch the magic happen!</b>")
        cta.setStyleSheet("color: #10B981; font-size: 13px; margin-top: 12px;")
        cta.setAlignment(Qt.AlignCenter)
        cta.setWordWrap(True)
        cta.setTextFormat(Qt.RichText)
        layout.addWidget(cta)

        layout.addStretch()

        return widget

    def create_shortcuts_step(self) -> QWidget:
        """Create keyboard shortcuts step"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Title
        title = QLabel("⌨️ Keyboard Ninja")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #7C3AED;")
        layout.addWidget(title)

        # Description
        desc = QLabel("Work faster with these essential shortcuts:")
        desc.setStyleSheet("font-size: 14px; color: #A0A0AB;")
        layout.addWidget(desc)

        # Shortcuts table
        shortcuts = [
            ("Ctrl+N", "New Note"),
            ("Ctrl+S", "Save Note"),
            ("Ctrl+F", "Find"),
            ("Ctrl+B", "Toggle Sidebar"),
            ("Ctrl+P", "Toggle Preview"),
            ("Ctrl+Shift+F", "Focus Mode"),
            ("Ctrl+Shift+A", "AI Assistant"),
            ("?", "Show All Shortcuts"),
        ]

        shortcuts_layout = QVBoxLayout()
        for shortcut, description in shortcuts:
            shortcut_widget = QWidget()
            shortcut_widget.setStyleSheet("""
                background-color: #2D2D3F;
                border-radius: 4px;
                padding: 8px;
                margin: 2px 0;
            """)
            shortcut_layout = QHBoxLayout(shortcut_widget)
            shortcut_layout.setContentsMargins(12, 6, 12, 6)

            key_label = QLabel(shortcut)
            key_label.setStyleSheet("""
                background-color: #1E1E2E;
                color: #7C3AED;
                font-family: monospace;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 12px;
            """)
            shortcut_layout.addWidget(key_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #E0E0E6; font-size: 13px;")
            shortcut_layout.addWidget(desc_label)

            shortcut_layout.addStretch()

            shortcuts_layout.addWidget(shortcut_widget)

        layout.addLayout(shortcuts_layout)

        # Tip
        tip = QLabel("💡 <b>Pro Tip:</b> Press <code>?</code> anytime to see all shortcuts")
        tip.setStyleSheet("color: #EC4899; font-size: 12px; margin-top: 12px;")
        tip.setAlignment(Qt.AlignCenter)
        tip.setWordWrap(True)
        tip.setTextFormat(Qt.RichText)
        layout.addWidget(tip)

        layout.addStretch()

        return widget

    def create_complete_step(self) -> QWidget:
        """Create completion step"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)

        # Success icon/title
        title = QLabel("🎉 You're All Set!")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #10B981;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Message
        message = QLabel("You're ready to start your learning journey with FlowNotes!")
        message.setStyleSheet("font-size: 16px; color: #E0E0E6;")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)

        # Next steps
        next_steps = QLabel("""
<div style='font-size: 14px; line-height: 1.8; text-align: center;'>
<p><b style='color: #7C3AED;'>What to do next:</b></p>
<ol style='text-align: left; display: inline-block; margin-left: 20px;'>
    <li>Create your first note (Ctrl+N)</li>
    <li>Try the AI assistant (right panel)</li>
    <li>Generate flashcards and review them</li>
    <li>Explore topics and search features</li>
</ol>
</div>
        """)
        next_steps.setTextFormat(Qt.RichText)
        next_steps.setWordWrap(True)
        layout.addWidget(next_steps)

        # Resources
        resources = QLabel("""
<div style='font-size: 12px; color: #A0A0AB; text-align: center;'>
<p><b>Need help?</b></p>
<p>Press <code>F1</code> for help • Join our Discord • Read the docs</p>
</div>
        """)
        resources.setTextFormat(Qt.RichText)
        resources.setAlignment(Qt.AlignCenter)
        resources.setWordWrap(True)
        layout.addWidget(resources)

        layout.addStretch()

        return widget

    def next_step(self):
        """Go to next step"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.steps_widget.setCurrentIndex(self.current_step)
            self.update_navigation()

    def previous_step(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.steps_widget.setCurrentIndex(self.current_step)
            self.update_navigation()

    def update_navigation(self):
        """Update navigation buttons"""
        self.back_button.setEnabled(self.current_step > 0)

        if self.current_step == self.total_steps - 1:
            self.next_button.setText("Get Started! →")
            self.next_button.clicked.disconnect()
            self.next_button.clicked.connect(lambda: self.finish_onboarding(True))
        else:
            if "Get Started" in self.next_button.text():
                self.next_button.setText("Next →")
                self.next_button.clicked.disconnect()
                self.next_button.clicked.connect(self.next_step)

        self.progress_label.setText(f"Step {self.current_step + 1} of {self.total_steps}")

    def finish_onboarding(self, completed: bool):
        """Finish onboarding"""
        self.finished.emit(completed)
        self.accept()


# Test
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    dialog = OnboardingDialog()
    dialog.finished.connect(lambda completed: print(f"Onboarding {'completed' if completed else 'skipped'}"))
    dialog.exec()

    sys.exit(0)
