"""
Smart Topic Selection for Consolidation

Provides interactive topic selection with:
- Fuzzy matching (type "web" to find "web-development", "web-scraping", etc.)
- Multiple topic selection
- Preview of what each topic contains
- Exclude/include modes
"""

from pathlib import Path
from typing import List, Set, Tuple
from difflib import SequenceMatcher
import re


class TopicSelector:
    """Interactive topic selector with fuzzy matching"""
    
    def __init__(self, topics_dir: Path):
        self.topics_dir = topics_dir
        self.available_topics = self._get_available_topics()
    
    def _get_available_topics(self) -> List[Tuple[str, int, str]]:
        """
        Get all available topics with metadata
        
        Returns:
            List of (topic_name, note_count, date_range)
        """
        topics = []
        
        if not self.topics_dir.exists():
            return topics
        
        for topic_dir in sorted(self.topics_dir.iterdir()):
            if not topic_dir.is_dir() or topic_dir.name.startswith('.'):
                continue
            
            # Count notes (check both raw/ and root level)
            raw_dir = topic_dir / "raw"
            if raw_dir.exists():
                note_files = list(raw_dir.glob("*.md"))
            else:
                note_files = list(topic_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
            
            if note_files:
                # Get date range
                dates = []
                for f in note_files:
                    # Extract date from filename
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.stem)
                    if date_match:
                        dates.append(date_match.group(1))
                
                date_range = f"{min(dates)} to {max(dates)}" if dates else "unknown"
                topics.append((topic_dir.name, len(note_files), date_range))
        
        return topics
    
    def fuzzy_match(self, query: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Find topics matching the query using fuzzy matching
        
        Args:
            query: Search term (e.g., "web", "pytorch", "ml")
            threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            List of (topic_name, similarity_score) sorted by score
        """
        query_lower = query.lower()
        matches = []
        
        for topic, count, date_range in self.available_topics:
            topic_lower = topic.lower()
            
            # Exact match
            if query_lower == topic_lower:
                matches.append((topic, 1.0, count, date_range))
                continue
            
            # Substring match
            if query_lower in topic_lower:
                # Higher score if query is at start
                if topic_lower.startswith(query_lower):
                    score = 0.9
                else:
                    score = 0.8
                matches.append((topic, score, count, date_range))
                continue
            
            # Fuzzy match using SequenceMatcher
            similarity = SequenceMatcher(None, query_lower, topic_lower).ratio()
            if similarity >= threshold:
                matches.append((topic, similarity, count, date_range))
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def interactive_select(
        self, 
        mode: str = "include",
        allow_multiple: bool = True,
        prompt: str = None
    ) -> List[str]:
        """
        Interactive topic selection with fuzzy matching
        
        Args:
            mode: "include" or "exclude"
            allow_multiple: Allow selecting multiple topics
            prompt: Custom prompt message
        
        Returns:
            List of selected topic names
        """
        if not self.available_topics:
            print("❌ No topics found")
            return []
        
        print("\n" + "=" * 80)
        print(f"TOPIC SELECTION - {mode.upper()} MODE")
        print("=" * 80)
        
        if prompt:
            print(f"\n{prompt}\n")
        
        selected_topics = []
        
        while True:
            print(f"\n📚 Available Topics ({len(self.available_topics)}):")
            self._show_topics_list(self.available_topics)
            
            print("\n💡 Tips:")
            print("  - Type part of a name for fuzzy search (e.g., 'web' finds 'web-development')")
            print("  - Type number to select by index")
            print("  - Type 'all' to select all topics")
            print("  - Type 'list' to see full list again")
            print("  - Type 'done' when finished" + (" (or press Enter)" if selected_topics else ""))
            
            if selected_topics:
                print(f"\n✓ Selected so far: {', '.join(selected_topics)}")
            
            choice = input(f"\n{mode.capitalize()} topic: ").strip()
            
            if not choice or choice.lower() == 'done':
                if selected_topics or not allow_multiple:
                    break
                else:
                    print("⚠ Please select at least one topic")
                    continue
            
            if choice.lower() == 'list':
                continue
            
            if choice.lower() == 'all':
                selected_topics = [topic for topic, _, _ in self.available_topics]
                print(f"✓ Selected all {len(selected_topics)} topics")
                break
            
            # Try to parse as number (index)
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.available_topics):
                    topic = self.available_topics[idx][0]
                    if topic not in selected_topics:
                        selected_topics.append(topic)
                        print(f"✓ Added: {topic}")
                    else:
                        print(f"⚠ Already selected: {topic}")
                else:
                    print(f"❌ Invalid index. Choose 1-{len(self.available_topics)}")
                
                if not allow_multiple:
                    break
                continue
            
            # Fuzzy search
            matches = self.fuzzy_match(choice)
            
            if not matches:
                print(f"❌ No topics found matching '{choice}'")
                continue
            
            if len(matches) == 1:
                # Single match - auto-select
                topic = matches[0][0]
                if topic not in selected_topics:
                    selected_topics.append(topic)
                    print(f"✓ Added: {topic}")
                else:
                    print(f"⚠ Already selected: {topic}")
                
                if not allow_multiple:
                    break
            else:
                # Multiple matches - show and let user choose
                print(f"\n🔍 Found {len(matches)} matching topics:")
                for i, (topic, score, count, date_range) in enumerate(matches, 1):
                    print(f"  {i}. {topic:<30} ({count} notes, {date_range})")
                
                sub_choice = input("\nSelect number (or Enter to cancel): ").strip()
                
                if sub_choice.isdigit():
                    idx = int(sub_choice) - 1
                    if 0 <= idx < len(matches):
                        topic = matches[idx][0]
                        if topic not in selected_topics:
                            selected_topics.append(topic)
                            print(f"✓ Added: {topic}")
                        else:
                            print(f"⚠ Already selected: {topic}")
                        
                        if not allow_multiple:
                            break
        
        return selected_topics
    
    def _show_topics_list(self, topics: List[Tuple[str, int, str]], max_display: int = 15):
        """Display topics with metadata"""
        for i, (topic, count, date_range) in enumerate(topics[:max_display], 1):
            print(f"  {i:2}. {topic:<30} ({count:3} notes, {date_range})")
        
        if len(topics) > max_display:
            print(f"  ... and {len(topics) - max_display} more (type 'list' to see all)")
    
    def select_with_preview(self, allow_multiple: bool = True) -> List[str]:
        """Select topics with content preview"""
        print("\n" + "=" * 80)
        print("TOPIC SELECTION WITH PREVIEW")
        print("=" * 80)
        
        while True:
            print(f"\n📚 Available Topics ({len(self.available_topics)}):")
            self._show_topics_list(self.available_topics)
            
            choice = input("\nEnter topic name/number to preview (or 'done'): ").strip()
            
            if choice.lower() == 'done':
                break
            
            # Convert to topic name
            topic_name = self._resolve_choice(choice)
            
            if not topic_name:
                print(f"❌ Topic not found: {choice}")
                continue
            
            # Show preview
            self._show_topic_preview(topic_name)
            
            # Ask if want to select
            select = input(f"\nInclude '{topic_name}' in consolidation? [Y/n]: ").strip().lower()
            
            if select != 'n':
                print(f"✓ Added: {topic_name}")
                # Continue selecting if allow_multiple
        
        return []
    
    def _resolve_choice(self, choice: str) -> str:
        """Resolve a choice to a topic name"""
        # Try number
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.available_topics):
                return self.available_topics[idx][0]
        
        # Try fuzzy match
        matches = self.fuzzy_match(choice)
        if matches and len(matches) == 1:
            return matches[0][0]
        
        # Try exact match
        for topic, _, _ in self.available_topics:
            if topic.lower() == choice.lower():
                return topic
        
        return None
    
    def _show_topic_preview(self, topic_name: str):
        """Show preview of topic content"""
        topic_dir = self.topics_dir / topic_name
        
        print("\n" + "-" * 80)
        print(f"PREVIEW: {topic_name}")
        print("-" * 80)
        
        # Get notes
        raw_dir = topic_dir / "raw"
        if raw_dir.exists():
            note_files = sorted(raw_dir.glob("*.md"))
        else:
            note_files = sorted(topic_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
        
        print(f"Notes: {len(note_files)}")
        
        if note_files:
            print(f"Date range: {note_files[0].stem[:10]} to {note_files[-1].stem[:10]}")
            
            # Show snippet from first note
            try:
                with open(note_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    preview = '\n'.join(lines[:5])
                    print(f"\nSnippet from first note:")
                    print(preview[:300] + "..." if len(preview) > 300 else preview)
            except:
                pass
        
        print("-" * 80)


def smart_topic_selection(
    topics_dir: Path,
    query: str = None,
    mode: str = "include",
    interactive: bool = True
) -> List[str]:
    """
    Smart topic selection - main entry point
    
    Args:
        topics_dir: Path to topics directory
        query: Optional search query for fuzzy matching
        mode: "include" or "exclude"
        interactive: If True, use interactive selection
    
    Returns:
        List of selected topic names
    """
    selector = TopicSelector(topics_dir)
    
    if not interactive and query:
        # Non-interactive: fuzzy match and return all matches
        matches = selector.fuzzy_match(query)
        return [topic for topic, score, _, _ in matches]
    
    if interactive:
        return selector.interactive_select(mode=mode, allow_multiple=True)
    
    return []
