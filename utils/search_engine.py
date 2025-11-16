"""
Full-text search engine for FlowNotes using Whoosh
Enables fast searching across all notes with ranking and filters
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime

try:
    from whoosh import index
    from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD
    from whoosh.qparser import QueryParser, MultifieldParser
    from whoosh.query import And, Or, Term
    from whoosh import scoring
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False

from utils.logger import get_logger

logger = get_logger(__name__)


class NoteSearchEngine:
    """Full-text search engine for notes"""

    def __init__(self, notes_dir: Path):
        """
        Initialize search engine

        Args:
            notes_dir: Base directory containing notes
        """
        if not WHOOSH_AVAILABLE:
            raise ImportError("Whoosh not available. Install with: pip install whoosh")

        self.notes_dir = Path(notes_dir)
        self.index_dir = self.notes_dir / ".search_index"
        self.index_dir.mkdir(exist_ok=True)

        # Define schema
        self.schema = Schema(
            note_id=ID(stored=True, unique=True),
            path=ID(stored=True),
            topic=TEXT(stored=True),
            title=TEXT(stored=True),
            content=TEXT,
            tags=KEYWORD(stored=True, commas=True),
            created=DATETIME(stored=True),
            modified=DATETIME(stored=True)
        )

        # Create or open index
        if index.exists_in(str(self.index_dir)):
            self.ix = index.open_dir(str(self.index_dir))
            logger.info("Opened existing search index")
        else:
            self.ix = index.create_in(str(self.index_dir), self.schema)
            logger.info("Created new search index")

    def index_note(
        self,
        note_path: Path,
        topic: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        created: Optional[datetime] = None,
        modified: Optional[datetime] = None
    ):
        """
        Add or update a note in the search index

        Args:
            note_path: Path to note file
            topic: Topic name
            title: Note title
            content: Note content
            tags: Optional list of tags
            created: Creation datetime
            modified: Modification datetime
        """
        writer = self.ix.writer()

        try:
            note_id = str(note_path.absolute())

            writer.update_document(
                note_id=note_id,
                path=str(note_path),
                topic=topic,
                title=title,
                content=content,
                tags=','.join(tags) if tags else '',
                created=created or datetime.now(),
                modified=modified or datetime.now()
            )

            writer.commit()
            logger.debug(f"Indexed note: {title}")

        except Exception as e:
            writer.cancel()
            logger.error(f"Failed to index note: {e}")
            raise

    def index_all_notes(self, force_rebuild: bool = False):
        """
        Index all notes in the notes directory

        Args:
            force_rebuild: If True, rebuild entire index from scratch
        """
        if force_rebuild:
            logger.info("Rebuilding search index from scratch")
            self.ix = index.create_in(str(self.index_dir), self.schema)

        topics_dir = self.notes_dir / "topics"
        if not topics_dir.exists():
            logger.warning(f"Topics directory not found: {topics_dir}")
            return

        indexed_count = 0

        for topic_dir in topics_dir.iterdir():
            if not topic_dir.is_dir():
                continue

            topic = topic_dir.name

            # Index markdown files
            for note_file in topic_dir.glob("*.md"):
                if note_file.name.startswith("learning-guide") or note_file.name.startswith("comments_"):
                    continue  # Skip generated files

                try:
                    content = note_file.read_text(encoding='utf-8')

                    # Extract title from first heading or filename
                    title = self._extract_title(content) or note_file.stem

                    # Extract tags
                    tags = self._extract_tags(content)

                    # Get file timestamps
                    stats = note_file.stat()
                    created = datetime.fromtimestamp(stats.st_ctime)
                    modified = datetime.fromtimestamp(stats.st_mtime)

                    self.index_note(
                        note_file, topic, title, content,
                        tags, created, modified
                    )

                    indexed_count += 1

                except Exception as e:
                    logger.error(f"Failed to index {note_file}: {e}")

        logger.info(f"Indexed {indexed_count} notes")

    def search(
        self,
        query_string: str,
        topic_filter: Optional[List[str]] = None,
        tag_filter: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Search notes with optional filters

        Args:
            query_string: Search query
            topic_filter: Optional list of topics to filter by
            tag_filter: Optional list of tags to filter by
            limit: Maximum number of results

        Returns:
            List of matching notes with metadata
        """
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            # Parse query across multiple fields
            parser = MultifieldParser(
                ["title", "content", "topic", "tags"],
                schema=self.schema
            )

            try:
                query = parser.parse(query_string)

                # Apply filters
                if topic_filter:
                    topic_queries = [Term("topic", t) for t in topic_filter]
                    topic_filter_query = Or(topic_queries)
                    query = And([query, topic_filter_query])

                if tag_filter:
                    tag_queries = [Term("tags", t) for t in tag_filter]
                    tag_filter_query = Or(tag_queries)
                    query = And([query, tag_filter_query])

                # Execute search
                results = searcher.search(query, limit=limit)

                # Format results
                formatted_results = []
                for hit in results:
                    formatted_results.append({
                        'path': hit['path'],
                        'topic': hit['topic'],
                        'title': hit['title'],
                        'tags': hit['tags'].split(',') if hit['tags'] else [],
                        'created': hit['created'],
                        'modified': hit['modified'],
                        'score': hit.score,
                        'highlights': hit.highlights("content", top=3)
                    })

                logger.info(f"Search '{query_string}' returned {len(formatted_results)} results")
                return formatted_results

            except Exception as e:
                logger.error(f"Search failed: {e}")
                return []

    def search_similar(
        self,
        note_path: Path,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find similar notes using More Like This

        Args:
            note_path: Path to reference note
            limit: Maximum number of similar notes

        Returns:
            List of similar notes
        """
        with self.ix.searcher() as searcher:
            try:
                note_id = str(note_path.absolute())

                # Find the note
                note = searcher.document(note_id=note_id)
                if not note:
                    logger.warning(f"Note not found in index: {note_path}")
                    return []

                # Get similar documents
                results = searcher.more_like(
                    note.docnum,
                    "content",
                    top=limit + 1  # +1 to exclude self
                )

                # Format results (skip first result if it's the same note)
                formatted_results = []
                for hit in results:
                    if hit['path'] != str(note_path):
                        formatted_results.append({
                            'path': hit['path'],
                            'topic': hit['topic'],
                            'title': hit['title'],
                            'tags': hit['tags'].split(',') if hit['tags'] else [],
                            'score': hit.score
                        })

                        if len(formatted_results) >= limit:
                            break

                logger.info(f"Found {len(formatted_results)} similar notes")
                return formatted_results

            except Exception as e:
                logger.error(f"Similar search failed: {e}")
                return []

    def get_all_topics(self) -> List[str]:
        """Get list of all indexed topics"""
        with self.ix.searcher() as searcher:
            topics = set()
            for fields in searcher.all_stored_fields():
                topics.add(fields.get('topic', ''))
            return sorted(list(topics))

    def get_all_tags(self) -> List[str]:
        """Get list of all indexed tags"""
        with self.ix.searcher() as searcher:
            tags = set()
            for fields in searcher.all_stored_fields():
                tag_str = fields.get('tags', '')
                if tag_str:
                    tags.update(tag_str.split(','))
            return sorted(list(tags))

    def get_stats(self) -> Dict:
        """Get search index statistics"""
        with self.ix.searcher() as searcher:
            return {
                'total_notes': searcher.doc_count_all(),
                'total_topics': len(self.get_all_topics()),
                'total_tags': len(self.get_all_tags()),
                'index_size_mb': self._get_index_size()
            }

    def _get_index_size(self) -> float:
        """Get total size of index directory in MB"""
        total_size = 0
        for file in self.index_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        return round(total_size / (1024 * 1024), 2)

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from markdown content"""
        import re
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extract_tags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        tags = re.findall(r'#(\w+)', content)
        return list(set(tags))

    def optimize(self):
        """Optimize the search index"""
        writer = self.ix.writer()
        writer.commit(optimize=True)
        logger.info("Search index optimized")


# CLI interface for search
def search_cli(notes_dir: Path):
    """Interactive search CLI"""
    engine = NoteSearchEngine(notes_dir)

    print("FlowNotes Search Engine")
    print("=" * 50)
    print(f"Index stats: {engine.get_stats()}")
    print("\nCommands:")
    print("  search <query>     - Search notes")
    print("  topics             - List all topics")
    print("  tags               - List all tags")
    print("  rebuild            - Rebuild search index")
    print("  quit               - Exit")
    print()

    while True:
        try:
            cmd = input("search> ").strip()

            if not cmd:
                continue

            if cmd == "quit":
                break

            elif cmd == "topics":
                topics = engine.get_all_topics()
                print(f"\nTopics ({len(topics)}):")
                for topic in topics:
                    print(f"  - {topic}")

            elif cmd == "tags":
                tags = engine.get_all_tags()
                print(f"\nTags ({len(tags)}):")
                for tag in tags:
                    print(f"  #{tag}")

            elif cmd == "rebuild":
                print("Rebuilding index...")
                engine.index_all_notes(force_rebuild=True)
                print(f"Done! {engine.get_stats()}")

            elif cmd.startswith("search "):
                query = cmd[7:].strip()
                results = engine.search(query, limit=10)

                print(f"\nResults ({len(results)}):\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. [{result['topic']}] {result['title']}")
                    print(f"   Score: {result['score']:.2f}")
                    if result['highlights']:
                        print(f"   ...{result['highlights']}...")
                    print()

            else:
                print("Unknown command. Type 'quit' to exit.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    notes_dir = Path.home() / "Projects" / "notes"

    if notes_dir.exists():
        # Test search engine
        engine = NoteSearchEngine(notes_dir)

        # Index all notes
        print("Indexing notes...")
        engine.index_all_notes()

        # Show stats
        print(f"\nStats: {engine.get_stats()}")

        # Run interactive search
        search_cli(notes_dir)
    else:
        print(f"Notes directory not found: {notes_dir}")
