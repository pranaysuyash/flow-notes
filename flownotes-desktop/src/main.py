#!/usr/bin/env python3
"""
FlowNotes Desktop Application
Main entry point for the PySide6 GUI application
"""

import sys
from pathlib import Path

# Add parent directory to path to import from utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon, QPalette, QColor
except ImportError:
    print("PySide6 not installed. Install with: pip install PySide6")
    sys.exit(1)

from ui.main_window import MainWindow
from utils.logger import get_logger

logger = get_logger(__name__)


def setup_application_style(app: QApplication):
    """Configure application-wide styling"""
    # Use Fusion style for modern look
    app.setStyle("Fusion")

    # Dark theme palette
    dark_palette = QPalette()

    # Background colors
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 46))          # --bg-primary
    dark_palette.setColor(QPalette.WindowText, QColor(224, 224, 230))   # --text-primary
    dark_palette.setColor(QPalette.Base, QColor(38, 38, 55))            # --bg-secondary
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 63))   # --bg-tertiary
    dark_palette.setColor(QPalette.ToolTipBase, QColor(224, 224, 230))
    dark_palette.setColor(QPalette.ToolTipText, QColor(224, 224, 230))
    dark_palette.setColor(QPalette.Text, QColor(224, 224, 230))
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 63))
    dark_palette.setColor(QPalette.ButtonText, QColor(224, 224, 230))
    dark_palette.setColor(QPalette.BrightText, Qt.red)

    # Accent colors
    dark_palette.setColor(QPalette.Highlight, QColor(124, 58, 237))     # --accent-primary (purple)
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

    # Links
    dark_palette.setColor(QPalette.Link, QColor(124, 58, 237))
    dark_palette.setColor(QPalette.LinkVisited, QColor(236, 72, 153))   # --accent-secondary (pink)

    app.setPalette(dark_palette)

    # Application stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1E1E2E;
        }

        QTextEdit, QPlainTextEdit {
            background-color: #262637;
            color: #E0E0E6;
            border: 1px solid #3A3A4F;
            border-radius: 6px;
            padding: 8px;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 13px;
        }

        QPushButton {
            background-color: #7C3AED;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #8B5CF6;
        }

        QPushButton:pressed {
            background-color: #6D28D9;
        }

        QPushButton:disabled {
            background-color: #3A3A4F;
            color: #70707A;
        }

        QListWidget {
            background-color: #262637;
            color: #E0E0E6;
            border: 1px solid #3A3A4F;
            border-radius: 6px;
        }

        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }

        QListWidget::item:selected {
            background-color: #7C3AED;
            color: white;
        }

        QListWidget::item:hover {
            background-color: #2D2D3F;
        }

        QMenuBar {
            background-color: #1E1E2E;
            color: #E0E0E6;
        }

        QMenuBar::item:selected {
            background-color: #7C3AED;
        }

        QMenu {
            background-color: #262637;
            color: #E0E0E6;
            border: 1px solid #3A3A4F;
        }

        QMenu::item:selected {
            background-color: #7C3AED;
        }

        QStatusBar {
            background-color: #1E1E2E;
            color: #A0A0AB;
        }

        QSplitter::handle {
            background-color: #3A3A4F;
        }

        QScrollBar:vertical {
            border: none;
            background-color: #262637;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #7C3AED;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #8B5CF6;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QToolBar {
            background-color: #262637;
            border: 1px solid #3A3A4F;
            spacing: 4px;
            padding: 4px;
        }

        QLineEdit {
            background-color: #262637;
            color: #E0E0E6;
            border: 1px solid #3A3A4F;
            border-radius: 6px;
            padding: 6px;
        }

        QLineEdit:focus {
            border: 1px solid #7C3AED;
        }
    """)


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("FlowNotes")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("FlowNotes")
    app.setOrganizationDomain("flownotes.app")

    # Setup styling
    setup_application_style(app)

    # Create and show main window
    logger.info("Starting FlowNotes Desktop v3.0")
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
