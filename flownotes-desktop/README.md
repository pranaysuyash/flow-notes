# FlowNotes Desktop v3.0

Beautiful, local-first desktop application for AI-powered note-taking and learning.

## 🚀 Quick Start

### Installation

1. **Install Python dependencies:**
```bash
cd flownotes-desktop
pip install PySide6 PySide6-Addons markdown2
```

2. **Run the application:**
```bash
python src/main.py
```

## ✨ Features

### Currently Implemented (MVP)

- ✅ **Beautiful Dark Theme** - Modern UI with purple accents
- ✅ **Three-Pane Layout** - Sidebar, Editor, Preview
- ✅ **Markdown Editor** - Syntax highlighting and auto-completion
- ✅ **Live Preview** - See your notes rendered in real-time
- ✅ **Topic Organization** - Browse notes by topic
- ✅ **File Management** - Create, open, save notes
- ✅ **Keyboard Shortcuts** - Fast navigation and actions
- ✅ **Focus Mode** - Distraction-free fullscreen writing

### Coming Soon

- ⏳ **AI Assistant Panel** - One-click enhancements (Week 4-5)
- ⏳ **Flashcard Review** - Spaced repetition system (Week 6)
- ⏳ **Full-Text Search** - Whoosh-powered search (Week 8)
- ⏳ **Cloud Sync** - E2E encrypted sync (Week 9-10)
- ⏳ **Export Formats** - PDF, HTML, Anki (Week 4)

## 🎨 UI Design

### Color Palette (Dark Theme)

```
Background:   #1E1E2E (Deep navy)
Secondary:    #262637 (Elevated surfaces)
Tertiary:     #2D2D3F (Cards, panels)

Text Primary:   #E0E0E6
Text Secondary: #A0A0AB
Text Tertiary:  #70707A

Accent Purple:  #7C3AED (Primary actions)
Accent Pink:    #EC4899 (Highlights)
Accent Green:   #10B981 (Success)
```

### Typography

- **Headers:** Inter (System fallback)
- **Body:** Georgia (Serif for readability)
- **Code:** JetBrains Mono (Monospace with ligatures)

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Note |
| `Ctrl+S` | Save Note |
| `Ctrl+O` | Open Note |
| `Ctrl+F` | Find |
| `Ctrl+B` | Toggle Sidebar |
| `Ctrl+P` | Toggle Preview |
| `Ctrl+Shift+F` | Focus Mode |
| `Ctrl+Shift+A` | AI Assistant |
| `Ctrl+Shift+S` | Generate Summary |
| `Ctrl+Shift+D` | Generate Diagram |
| `Ctrl+Shift+Q` | Generate Quiz |

## 📁 Project Structure

```
flownotes-desktop/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui/
│   │   ├── main_window.py   # Main window with menus
│   │   ├── sidebar.py       # Topic/note navigation
│   │   ├── editor.py        # Markdown editor
│   │   └── preview.py       # Live preview pane
│   ├── core/
│   │   └── (Coming soon)    # Note management logic
│   ├── ai/
│   │   └── (Coming soon)    # LLM integration
│   └── utils/
│       └── (Coming soon)    # Helper utilities
├── resources/
│   └── (Coming soon)        # Icons, themes
└── README.md
```

## 🛠️ Development

### Running in Development Mode

```bash
# Activate virtual environment
cd flownotes-desktop
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install PySide6 PySide6-Addons markdown2

# Run app
python src/main.py
```

### Building Standalone App

**macOS (DMG):**
```bash
pip install py2app
python setup.py py2app
```

**Windows (MSI):**
```bash
pip install cx_Freeze
python setup.py bdist_msi
```

**Linux (AppImage):**
```bash
pip install PyInstaller
pyinstaller --onefile --windowed src/main.py
```

## 🐛 Known Issues

- [ ] Mermaid diagrams not yet rendered in preview
- [ ] Search functionality not implemented
- [ ] AI features are placeholders
- [ ] No auto-save indicator

## 🎯 Roadmap

See [IMPLEMENTATION_ROADMAP_V3.md](../IMPLEMENTATION_ROADMAP_V3.md) for the full development roadmap.

### Next Milestones

**Week 4-5:** AI Integration
- Connect to LLM services
- Implement one-click enhancements
- Add AI assistant panel

**Week 6-7:** Learning Features
- Flashcard system with spaced repetition
- Learning dashboard with statistics
- Review scheduler

**Week 8:** Search & Discovery
- Full-text search with Whoosh
- Semantic search
- Related notes suggestions

## 📝 Contributing

FlowNotes Desktop is part of the larger FlowNotes project. See the main project README for contribution guidelines.

## 📄 License

MIT License - see LICENSE file for details.

---

**Made with ❤️ for learners, by learners**

Transform your notes into comprehensive learning guides with AI-powered intelligence!
