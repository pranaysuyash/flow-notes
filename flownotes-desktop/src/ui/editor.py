"""
Note Editor component for FlowNotes Desktop
Markdown editor with syntax highlighting and auto-save
"""

import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QPlainTextEdit
    from PySide6.QtCore import Signal, QTimer, Qt
    from PySide6.QtGui import (
        QSyntaxHighlighter, QTextCharFormat, QFont,
        QColor, QTextDocument
    )
except ImportError:
    print("PySide6 not installed")
    raise


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Markdown"""

    def __init__(self, parent: QTextDocument):
        super().__init__(parent)

        self.highlighting_rules = []

        # Headers
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#7C3AED"))  # Purple
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'^#{1,6}\s.*', header_format))

        # Bold
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\*\*.*?\*\*', bold_format))
        self.highlighting_rules.append((r'__.*?__', bold_format))

        # Italic
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*.*?\*', italic_format))
        self.highlighting_rules.append((r'_.*?_', italic_format))

        # Code inline
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#EC4899"))  # Pink
        code_format.setBackground(QColor("#2D2D3F"))
        self.highlighting_rules.append((r'`.*?`', code_format))

        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#3B82F6"))  # Blue
        link_format.setFontUnderline(True)
        self.highlighting_rules.append((r'\[.*?\]\(.*?\)', link_format))

        # Lists
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#10B981"))  # Green
        self.highlighting_rules.append((r'^\s*[-*+]\s', list_format))
        self.highlighting_rules.append((r'^\s*\d+\.\s', list_format))

        # Blockquotes
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#A0A0AB"))  # Gray
        quote_format.setFontItalic(True)
        self.highlighting_rules.append((r'^>\s.*', quote_format))

    def highlightBlock(self, text: str):
        """Highlight a block of text"""
        import re

        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text, re.MULTILINE):
                self.setFormat(match.start(), match.end() - match.start(), format)


class NoteEditor(QPlainTextEdit):
    """Markdown editor with auto-save and syntax highlighting"""

    # Signals
    content_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setup_editor()
        self.setup_auto_save()

    def setup_editor(self):
        """Setup editor properties"""
        # Font
        font = QFont("JetBrains Mono", 13)
        if not font.exactMatch():
            font = QFont("Courier New", 13)
        self.setFont(font)

        # Syntax highlighting
        self.highlighter = MarkdownHighlighter(self.document())

        # Tab behavior
        self.setTabStopDistance(40)  # 4 spaces

        # Placeholder
        self.setPlaceholderText("Start typing your notes here...\n\nMarkdown is supported:\n# Headers\n**bold** *italic*\n- Lists\n[links](url)\n```code```")

        # Connect signals
        self.textChanged.connect(self.on_text_changed)

    def setup_auto_save(self):
        """Setup auto-save timer"""
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(3000)  # Auto-save every 3 seconds

    def on_text_changed(self):
        """Handle text changes"""
        self.content_changed.emit()

    def auto_save(self):
        """Auto-save current content"""
        # This will be connected to the main window's save function
        if self.document().isModified():
            # Signal that auto-save should happen
            pass

    def keyPressEvent(self, event):
        """Handle key press events"""
        # Custom key handling (e.g., smart indentation)
        if event.key() == Qt.Key_Tab:
            # Insert spaces instead of tab
            self.insertPlainText("    ")
        else:
            super().keyPressEvent(event)
