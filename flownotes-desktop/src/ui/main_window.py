"""
Main Window for FlowNotes Desktop
Contains the primary application layout with sidebar, editor, and preview
"""

from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QStatusBar, QMenuBar, QMenu, QToolBar,
        QMessageBox, QFileDialog
    )
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QAction, QKeySequence, QIcon
except ImportError:
    print("PySide6 not installed")
    raise

from ui.sidebar import Sidebar
from ui.editor import NoteEditor
from ui.preview import MarkdownPreview


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.notes_dir = Path.home() / "Projects" / "notes"
        self.current_note_path = None

        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

        # Window settings
        self.setWindowTitle("FlowNotes - AI-Powered Learning")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)

    def setup_ui(self):
        """Setup the user interface layout"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter (sidebar | content)
        main_splitter = QSplitter(Qt.Horizontal)

        # Sidebar (topics, search, etc.)
        self.sidebar = Sidebar(self.notes_dir)
        self.sidebar.note_selected.connect(self.load_note)
        self.sidebar.new_note_requested.connect(self.create_new_note)

        # Content splitter (editor | preview)
        content_splitter = QSplitter(Qt.Horizontal)

        # Editor
        self.editor = NoteEditor()
        self.editor.content_changed.connect(self.on_content_changed)

        # Preview
        self.preview = MarkdownPreview()

        # Add to content splitter
        content_splitter.addWidget(self.editor)
        content_splitter.addWidget(self.preview)
        content_splitter.setSizes([600, 400])  # 60/40 split

        # Add to main splitter
        main_splitter.addWidget(self.sidebar)
        main_splitter.addWidget(content_splitter)
        main_splitter.setSizes([250, 1150])  # Sidebar smaller

        # Add to main layout
        main_layout.addWidget(main_splitter)

    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_note_action = QAction("&New Note", self)
        new_note_action.setShortcut(QKeySequence.New)
        new_note_action.triggered.connect(self.create_new_note)
        file_menu.addAction(new_note_action)

        open_action = QAction("&Open Note...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_note)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_note)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("Export")

        export_pdf_action = QAction("Export to PDF...", self)
        export_pdf_action.triggered.connect(lambda: self.export_note("pdf"))
        export_menu.addAction(export_pdf_action)

        export_html_action = QAction("Export to HTML...", self)
        export_html_action.triggered.connect(lambda: self.export_note("html"))
        export_menu.addAction(export_html_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        toggle_preview_action = QAction("Toggle &Preview", self)
        toggle_preview_action.setShortcut("Ctrl+P")
        toggle_preview_action.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview_action)

        view_menu.addSeparator()

        focus_mode_action = QAction("&Focus Mode", self)
        focus_mode_action.setShortcut("Ctrl+Shift+F")
        focus_mode_action.triggered.connect(self.toggle_focus_mode)
        view_menu.addAction(focus_mode_action)

        # AI menu
        ai_menu = menubar.addMenu("&AI")

        generate_summary_action = QAction("Generate &Summary", self)
        generate_summary_action.setShortcut("Ctrl+Shift+S")
        generate_summary_action.triggered.connect(lambda: self.ai_enhancement("summary"))
        ai_menu.addAction(generate_summary_action)

        generate_diagram_action = QAction("Generate &Diagram", self)
        generate_diagram_action.setShortcut("Ctrl+Shift+D")
        generate_diagram_action.triggered.connect(lambda: self.ai_enhancement("diagram"))
        ai_menu.addAction(generate_diagram_action)

        generate_quiz_action = QAction("Generate &Quiz", self)
        generate_quiz_action.setShortcut("Ctrl+Shift+Q")
        generate_quiz_action.triggered.connect(lambda: self.ai_enhancement("quiz"))
        ai_menu.addAction(generate_quiz_action)

        generate_flashcards_action = QAction("Generate &Flashcards", self)
        generate_flashcards_action.triggered.connect(lambda: self.ai_enhancement("flashcards"))
        ai_menu.addAction(generate_flashcards_action)

        ai_menu.addSeparator()

        ai_assistant_action = QAction("Show AI &Assistant", self)
        ai_assistant_action.setShortcut("Ctrl+Shift+A")
        ai_assistant_action.triggered.connect(self.show_ai_assistant)
        ai_menu.addAction(ai_assistant_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About FlowNotes", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)

    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Add actions
        new_note_action = QAction("New", self)
        new_note_action.triggered.connect(self.create_new_note)
        toolbar.addAction(new_note_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_note)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # AI quick actions
        ai_enhance_action = QAction("AI Enhance", self)
        ai_enhance_action.triggered.connect(lambda: self.ai_enhancement("all"))
        toolbar.addAction(ai_enhance_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    # Slots (event handlers)

    def load_note(self, note_path: Path):
        """Load a note into the editor"""
        try:
            content = note_path.read_text(encoding='utf-8')
            self.editor.setPlainText(content)
            self.current_note_path = note_path
            self.preview.update_preview(content)
            self.status_bar.showMessage(f"Loaded: {note_path.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load note: {e}")

    def create_new_note(self):
        """Create a new note"""
        self.editor.clear()
        self.current_note_path = None
        self.status_bar.showMessage("New note")

    def save_note(self):
        """Save the current note"""
        if not self.current_note_path:
            # Ask for filename
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Note",
                str(self.notes_dir / "topics"),
                "Markdown Files (*.md)"
            )

            if not file_path:
                return

            self.current_note_path = Path(file_path)

        try:
            content = self.editor.toPlainText()
            self.current_note_path.write_text(content, encoding='utf-8')
            self.status_bar.showMessage(f"Saved: {self.current_note_path.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note: {e}")

    def open_note(self):
        """Open a note file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Note",
            str(self.notes_dir / "topics"),
            "Markdown Files (*.md)"
        )

        if file_path:
            self.load_note(Path(file_path))

    def on_content_changed(self):
        """Handle editor content changes"""
        content = self.editor.toPlainText()
        self.preview.update_preview(content)

        # Update status bar with word count
        word_count = len(content.split())
        self.status_bar.showMessage(f"Words: {word_count}")

    def export_note(self, format_type: str):
        """Export note to specified format"""
        QMessageBox.information(
            self,
            "Export",
            f"Export to {format_type.upper()} - Coming soon!"
        )

    def ai_enhancement(self, enhancement_type: str):
        """Trigger AI enhancement"""
        QMessageBox.information(
            self,
            "AI Enhancement",
            f"Generating {enhancement_type} - Coming soon!"
        )

    def show_ai_assistant(self):
        """Show AI assistant panel"""
        QMessageBox.information(
            self,
            "AI Assistant",
            "AI Assistant panel - Coming soon!"
        )

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def toggle_preview(self):
        """Toggle preview pane visibility"""
        self.preview.setVisible(not self.preview.isVisible())

    def toggle_focus_mode(self):
        """Toggle distraction-free focus mode"""
        is_fullscreen = self.isFullScreen()

        if is_fullscreen:
            self.showNormal()
            self.sidebar.show()
            self.preview.show()
            self.menuBar().show()
            self.statusBar().show()
        else:
            self.showFullScreen()
            self.sidebar.hide()
            self.preview.hide()
            self.menuBar().hide()
            self.statusBar().hide()

    def show_find_dialog(self):
        """Show find/replace dialog"""
        QMessageBox.information(self, "Find", "Find dialog - Coming soon!")

    def show_about_dialog(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About FlowNotes",
            "<h2>FlowNotes v3.0</h2>"
            "<p>AI-Powered Learning Companion</p>"
            "<p>Transform your notes into comprehensive learning materials</p>"
            "<p><a href='https://flownotes.app'>flownotes.app</a></p>"
        )

    def show_shortcuts_dialog(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>New Note</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save Note</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open Note</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Find</td></tr>
        <tr><td><b>Ctrl+B</b></td><td>Toggle Sidebar</td></tr>
        <tr><td><b>Ctrl+P</b></td><td>Toggle Preview</td></tr>
        <tr><td><b>Ctrl+Shift+F</b></td><td>Focus Mode</td></tr>
        <tr><td><b>Ctrl+Shift+A</b></td><td>AI Assistant</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Generate Summary</td></tr>
        <tr><td><b>Ctrl+Shift+D</b></td><td>Generate Diagram</td></tr>
        <tr><td><b>Ctrl+Shift+Q</b></td><td>Generate Quiz</td></tr>
        </table>
        """

        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)

    def closeEvent(self, event):
        """Handle window close event"""
        # Check for unsaved changes
        if self.editor.document().isModified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_note()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
