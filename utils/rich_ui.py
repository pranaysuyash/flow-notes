"""
Rich Terminal UI utilities for FlowNotes
Beautiful, colorful terminal interface with progress bars and panels
"""

from typing import List, Dict, Optional
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichUI:
    """Beautiful terminal UI using Rich library"""

    def __init__(self):
        if not RICH_AVAILABLE:
            raise ImportError("Rich not available. Install with: pip install rich")

        self.console = Console()

    def print_header(self, title: str = "FlowNotes", subtitle: str = "AI-Powered Learning"):
        """Print application header"""
        header_text = f"[bold cyan]{title}[/]\n[dim]{subtitle}[/]"
        self.console.print(Panel(header_text, border_style="cyan", padding=(1, 2)))

    def print_markdown(self, content: str):
        """Render markdown content"""
        md = Markdown(content)
        self.console.print(md)

    def print_code(self, code: str, language: str = "python"):
        """Print syntax-highlighted code"""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(syntax)

    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"[green]✓[/] {message}")

    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"[red]✗[/] {message}")

    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"[yellow]⚠[/] {message}")

    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"[blue]ℹ[/] {message}")

    def create_table(
        self,
        title: str,
        columns: List[str],
        rows: List[List[str]],
        show_header: bool = True
    ) -> Table:
        """Create a formatted table"""
        table = Table(title=title, show_header=show_header)

        for col in columns:
            table.add_column(col, style="cyan")

        for row in rows:
            table.add_row(*row)

        return table

    def print_topic_list(self, topics: List[Dict[str, any]]):
        """Print formatted list of topics with stats"""
        table = Table(title="📚 Topics", show_header=True, header_style="bold magenta")

        table.add_column("Topic", style="cyan", no_wrap=True)
        table.add_column("Notes", justify="right", style="green")
        table.add_column("Words", justify="right", style="yellow")
        table.add_column("Last Updated", style="blue")

        for topic in topics:
            table.add_row(
                topic.get('name', ''),
                str(topic.get('note_count', 0)),
                f"{topic.get('word_count', 0):,}",
                topic.get('last_updated', 'N/A')
            )

        self.console.print(table)

    def print_search_results(self, results: List[Dict[str, any]]):
        """Print formatted search results"""
        if not results:
            self.print_warning("No results found")
            return

        self.console.print(f"\n[bold]Found {len(results)} results:[/]\n")

        for i, result in enumerate(results, 1):
            # Create result panel
            title = f"[cyan]{result.get('title', 'Untitled')}[/]"
            topic = f"[dim]{result.get('topic', 'Unknown')}[/]"
            score = f"[green]Relevance: {result.get('score', 0):.0%}[/]"

            header = f"{i}. {title} · {topic} · {score}"

            # Highlights
            highlights = result.get('highlights', '')
            if highlights:
                content = f"...{highlights}..."
            else:
                content = "[dim]No preview available[/]"

            self.console.print(Panel(content, title=header, border_style="blue"))

    def prompt_input(self, message: str, default: Optional[str] = None) -> str:
        """Get user input with rich prompt"""
        return Prompt.ask(f"[cyan]{message}[/]", default=default)

    def prompt_confirm(self, message: str, default: bool = True) -> bool:
        """Get yes/no confirmation"""
        return Confirm.ask(f"[yellow]{message}[/]", default=default)

    def prompt_choice(self, message: str, choices: List[str]) -> str:
        """Get user choice from list"""
        return Prompt.ask(
            f"[cyan]{message}[/]",
            choices=choices,
            show_choices=True
        )

    def create_progress_bar(self, description: str = "Processing"):
        """Create a progress bar context manager"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )

    def print_learning_guide_preview(self, guide_data: Dict[str, str]):
        """Print beautiful preview of learning guide"""
        layout = Layout()

        # Split into sections
        sections = []

        if guide_data.get('tldr'):
            sections.append(Panel(
                guide_data['tldr'],
                title="[bold cyan]📋 TL;DR[/]",
                border_style="cyan"
            ))

        if guide_data.get('tags'):
            tags_formatted = ' '.join(f'[magenta]#{tag}[/]' for tag in guide_data['tags'])
            sections.append(Panel(
                tags_formatted,
                title="[bold magenta]🏷️  Tags[/]",
                border_style="magenta"
            ))

        if guide_data.get('quiz'):
            sections.append(Panel(
                guide_data['quiz'],
                title="[bold yellow]❓ Quiz Questions[/]",
                border_style="yellow"
            ))

        if guide_data.get('flashcards_count'):
            sections.append(Panel(
                f"[green]{guide_data['flashcards_count']} flashcards generated[/]",
                title="[bold green]🗂️  Flashcards[/]",
                border_style="green"
            ))

        # Print all sections
        for section in sections:
            self.console.print(section)
            self.console.print()

    def print_stats_dashboard(self, stats: Dict[str, any]):
        """Print statistics dashboard"""
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # Header
        header_panel = Panel(
            "[bold cyan]📊 Learning Statistics[/]",
            style="cyan"
        )

        # Stats table
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan", width=30)
        stats_table.add_column("Value", style="green", justify="right")

        stats_table.add_row("Total Notes", str(stats.get('total_notes', 0)))
        stats_table.add_row("Topics", str(stats.get('topics', 0)))
        stats_table.add_row("Flashcards", str(stats.get('flashcards', 0)))
        stats_table.add_row("Study Streak", f"{stats.get('streak_days', 0)} days 🔥")
        stats_table.add_row("This Week", f"{stats.get('notes_this_week', 0)} notes")

        self.console.print(header_panel)
        self.console.print(stats_table)

    def print_file_tree(self, root_path: Path, max_depth: int = 3):
        """Print directory tree structure"""
        tree = Tree(
            f"[bold cyan]{root_path.name}[/]",
            guide_style="cyan"
        )

        def add_directory(path: Path, parent_tree: Tree, depth: int = 0):
            if depth >= max_depth:
                return

            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

                for item in items:
                    if item.name.startswith('.'):
                        continue

                    if item.is_dir():
                        branch = parent_tree.add(f"[blue]{item.name}/[/]")
                        add_directory(item, branch, depth + 1)
                    else:
                        parent_tree.add(f"[green]{item.name}[/]")
            except PermissionError:
                parent_tree.add("[red]Permission denied[/]")

        add_directory(root_path, tree)
        self.console.print(tree)

    def show_consolidation_preview(self, preview_data: Dict[str, any]):
        """Show preview before consolidation"""
        self.console.print()
        self.console.print("[bold cyan]" + "="*60 + "[/]")
        self.console.print("[bold cyan]CONSOLIDATION PREVIEW[/]")
        self.console.print("[bold cyan]" + "="*60 + "[/]")
        self.console.print()

        info = [
            f"Mode: [cyan]{preview_data.get('mode', 'N/A')}[/]",
            f"Topics: [cyan]{', '.join(preview_data.get('topics', []))}[/]",
            f"Total notes: [green]{preview_data.get('note_count', 0)}[/]",
            f"Date range: [yellow]{preview_data.get('date_range', 'N/A')}[/]",
        ]

        if preview_data.get('duplicate_detection'):
            info.append(f"Duplicate detection: [yellow]ON[/] (threshold: {preview_data.get('duplicate_threshold', 0.7)})")

        for line in info:
            self.console.print(f"  {line}")

        self.console.print()
        self.console.print("[bold cyan]" + "="*60 + "[/]")
        self.console.print()


# Convenience functions
def get_rich_ui() -> RichUI:
    """Get RichUI instance"""
    return RichUI()


# Example usage and demo
if __name__ == "__main__":
    ui = RichUI()

    # Header
    ui.print_header("FlowNotes", "v2.5 - Enhanced Edition")

    # Success/Error messages
    ui.print_success("Notes indexed successfully")
    ui.print_error("Failed to connect to API")
    ui.print_warning("Rate limit approaching")
    ui.print_info("Tip: Use Ctrl+D to finish input")

    print()

    # Markdown
    markdown_content = """
# Welcome to FlowNotes

This is a **powerful** note-taking system with:

- AI-powered enhancements
- Beautiful terminal UI
- Export to multiple formats

## Get Started

1. Take notes
2. Say "done for the day"
3. Get comprehensive learning guide
"""
    ui.print_markdown(markdown_content)

    print()

    # Table
    topics = [
        {'name': 'Machine Learning', 'note_count': 24, 'word_count': 12450, 'last_updated': '2024-11-16'},
        {'name': 'Python', 'note_count': 18, 'word_count': 8200, 'last_updated': '2024-11-15'},
        {'name': 'Deep Learning', 'note_count': 15, 'word_count': 9800, 'last_updated': '2024-11-14'},
    ]
    ui.print_topic_list(topics)

    print()

    # Code
    code_example = """
def consolidate_notes(notes):
    \"\"\"Generate learning guide\"\"\"
    return enhance_with_ai(notes)
"""
    ui.print_code(code_example, "python")

    print()

    # Progress bar
    print("Progress bar demo:")
    with ui.create_progress_bar("Processing notes") as progress:
        task = progress.add_task("Consolidating...", total=100)

        import time
        for i in range(100):
            progress.update(task, advance=1)
            time.sleep(0.01)

    print()

    # Stats dashboard
    stats = {
        'total_notes': 127,
        'topics': 8,
        'flashcards': 234,
        'streak_days': 12,
        'notes_this_week': 15
    }
    ui.print_stats_dashboard(stats)

    print()

    # Interactive prompts
    # name = ui.prompt_input("What's your name?", default="User")
    # confirm = ui.prompt_confirm("Do you want to continue?")
    # choice = ui.prompt_choice("Choose a format", ["PDF", "HTML", "Markdown"])

    print("\nRich UI demo complete!")
