"""
Sidebar component for FlowNotes Desktop
Shows topics, notes, and search functionality
"""

from pathlib import Path
from typing import List

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
        QLineEdit, QPushButton, QLabel, QTabWidget
    )
    from PySide6.QtCore import Signal, Qt
except ImportError:
    print("PySide6 not installed")
    raise


class Sidebar(QWidget):
    """Sidebar with topics and search"""

    # Signals
    note_selected = Signal(Path)
    new_note_requested = Signal()

    def __init__(self, notes_dir: Path):
        super().__init__()

        self.notes_dir = notes_dir
        self.topics_dir = notes_dir / "topics"

        self.setup_ui()
        self.load_topics()

    def setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search notes...")
        self.search_box.textChanged.connect(self.on_search)
        layout.addWidget(self.search_box)

        # New note button
        self.new_note_btn = QPushButton("+ New Note")
        self.new_note_btn.clicked.connect(self.new_note_requested.emit)
        layout.addWidget(self.new_note_btn)

        # Tabs for different views
        self.tabs = QTabWidget()

        # Topics tab
        self.topics_list = QListWidget()
        self.topics_list.itemClicked.connect(self.on_topic_clicked)
        self.tabs.addTab(self.topics_list, "📚 Topics")

        # Recent tab
        self.recent_list = QListWidget()
        self.recent_list.itemClicked.connect(self.on_note_clicked)
        self.tabs.addTab(self.recent_list, "🕒 Recent")

        # Tags tab
        self.tags_list = QListWidget()
        self.tabs.addTab(self.tags_list, "🏷️ Tags")

        layout.addWidget(self.tabs)

        # Stats label
        self.stats_label = QLabel("Ready")
        self.stats_label.setStyleSheet("color: #A0A0AB; font-size: 11px;")
        layout.addWidget(self.stats_label)

    def load_topics(self):
        """Load topics from directory"""
        self.topics_list.clear()

        if not self.topics_dir.exists():
            return

        topics = [d for d in self.topics_dir.iterdir() if d.is_dir()]

        for topic_dir in sorted(topics):
            # Count notes in topic
            notes = list(topic_dir.glob("*.md"))
            note_count = len([n for n in notes if not n.name.startswith(('learning-guide', 'comments_'))])

            item = QListWidgetItem(f"{topic_dir.name} ({note_count})")
            item.setData(Qt.UserRole, topic_dir)
            self.topics_list.addItem(item)

        self.update_stats()

    def on_topic_clicked(self, item: QListWidgetItem):
        """Handle topic selection"""
        topic_dir = item.data(Qt.UserRole)

        # Load notes from topic
        self.recent_list.clear()

        notes = sorted(
            topic_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for note_path in notes:
            if note_path.name.startswith(('learning-guide', 'comments_')):
                continue

            note_item = QListWidgetItem(note_path.stem)
            note_item.setData(Qt.UserRole, note_path)
            self.recent_list.addItem(note_item)

        # Switch to recent tab
        self.tabs.setCurrentIndex(1)

    def on_note_clicked(self, item: QListWidgetItem):
        """Handle note selection"""
        note_path = item.data(Qt.UserRole)
        self.note_selected.emit(note_path)

    def on_search(self, text: str):
        """Handle search input"""
        # TODO: Implement search functionality
        pass

    def update_stats(self):
        """Update statistics label"""
        total_notes = 0
        total_topics = 0

        if self.topics_dir.exists():
            for topic_dir in self.topics_dir.iterdir():
                if topic_dir.is_dir():
                    total_topics += 1
                    notes = [n for n in topic_dir.glob("*.md")
                            if not n.name.startswith(('learning-guide', 'comments_'))]
                    total_notes += len(notes)

        self.stats_label.setText(f"{total_notes} notes · {total_topics} topics")
