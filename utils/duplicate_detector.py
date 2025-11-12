"""
Duplicate Detection Engine for Learning Mentor

Detects similar content across notes using multiple strategies:
1. Sentence embeddings (if available)
2. TF-IDF similarity (fallback)
3. Exact match detection
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NoteMetadata:
    """Metadata for a note"""
    filepath: Path
    timestamp: datetime
    topic: str
    source: Optional[str] = None  # Course name, session ID, etc.
    tags: List[str] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class DuplicateMatch:
    """Represents a potential duplicate"""
    note1: NoteMetadata
    note2: NoteMetadata
    similarity_score: float
    match_type: str  # 'exact', 'high', 'moderate', 'low'
    matching_segments: List[str]  # What content matches
    
    def __str__(self):
        return f"{self.match_type.upper()} ({self.similarity_score:.0%}): {self.note1.filepath.name} ↔ {self.note2.filepath.name}"


class DuplicateDetector:
    """Detects duplicate and similar content across notes"""
    
    def __init__(self, use_embeddings=True):
        self.use_embeddings = use_embeddings
        self.embeddings_available = False
        
        # Try to import sentence transformers
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
                self.embeddings_available = True
                print("✓ Using semantic embeddings for duplicate detection")
            except ImportError:
                print("⚠ sentence-transformers not available, using TF-IDF")
                self.embeddings_available = False
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0.0 to 1.0)"""
        if not text1.strip() or not text2.strip():
            return 0.0
        
        # Check for exact match first
        if text1.strip() == text2.strip():
            return 1.0
        
        if self.embeddings_available:
            return self._similarity_embeddings(text1, text2)
        else:
            return self._similarity_tfidf(text1, text2)
    
    def _similarity_embeddings(self, text1: str, text2: str) -> float:
        """Calculate similarity using sentence embeddings"""
        from sentence_transformers import util
        
        # Encode both texts
        embedding1 = self.model.encode(text1, convert_to_tensor=True)
        embedding2 = self.model.encode(text2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.cos_sim(embedding1, embedding2)
        return float(similarity[0][0])
    
    def _similarity_tfidf(self, text1: str, text2: str) -> float:
        """Calculate similarity using TF-IDF (fallback)"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        try:
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
            
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            # Ultra-simple fallback: word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            overlap = len(words1 & words2)
            return overlap / max(len(words1), len(words2))
    
    def find_duplicates(
        self, 
        notes: Dict[str, str],  # filepath -> content
        threshold: float = 0.7
    ) -> List[DuplicateMatch]:
        """
        Find all duplicate/similar notes above threshold
        
        Args:
            notes: Dictionary mapping file paths to note content
            threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            List of DuplicateMatch objects sorted by similarity
        """
        duplicates = []
        note_items = list(notes.items())
        
        # Compare each pair of notes
        for i in range(len(note_items)):
            for j in range(i + 1, len(note_items)):
                filepath1, content1 = note_items[i]
                filepath2, content2 = note_items[j]
                
                similarity = self.calculate_similarity(content1, content2)
                
                if similarity >= threshold:
                    # Categorize match type
                    if similarity >= 0.95:
                        match_type = 'exact'
                    elif similarity >= 0.80:
                        match_type = 'high'
                    elif similarity >= 0.60:
                        match_type = 'moderate'
                    else:
                        match_type = 'low'
                    
                    # Find matching segments (simplified)
                    matching_segments = self._find_matching_segments(content1, content2)
                    
                    # Create metadata (simplified - can be enhanced)
                    meta1 = self._create_metadata(filepath1)
                    meta2 = self._create_metadata(filepath2)
                    
                    duplicates.append(DuplicateMatch(
                        note1=meta1,
                        note2=meta2,
                        similarity_score=similarity,
                        match_type=match_type,
                        matching_segments=matching_segments
                    ))
        
        # Sort by similarity (highest first)
        duplicates.sort(key=lambda x: x.similarity_score, reverse=True)
        return duplicates
    
    def _find_matching_segments(self, text1: str, text2: str, min_length: int = 50) -> List[str]:
        """Find matching text segments between two texts"""
        # Simple implementation: find common sentences
        sentences1 = [s.strip() for s in re.split(r'[.!?]\s+', text1) if len(s.strip()) > min_length]
        sentences2 = [s.strip() for s in re.split(r'[.!?]\s+', text2) if len(s.strip()) > min_length]
        
        matching = []
        for s1 in sentences1:
            for s2 in sentences2:
                # Simple similarity check
                if s1 == s2 or self._sentence_similar(s1, s2):
                    matching.append(s1)
                    break
        
        return matching[:5]  # Return top 5 matches
    
    def _sentence_similar(self, s1: str, s2: str, threshold: float = 0.8) -> bool:
        """Check if two sentences are similar"""
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        if not words1 or not words2:
            return False
        overlap = len(words1 & words2)
        return overlap / min(len(words1), len(words2)) >= threshold
    
    def _create_metadata(self, filepath: str) -> NoteMetadata:
        """Create metadata from filepath (can be enhanced with actual metadata files)"""
        path = Path(filepath)
        
        # Extract info from path
        topic = path.parent.name if path.parent.name != 'raw' else path.parent.parent.name
        
        # Try to parse timestamp from filename
        try:
            # Assuming format: YYYY-MM-DD_HH-MM-SS.md or YYYY-MM-DD.md
            date_part = path.stem.split('_')[0]
            timestamp = datetime.strptime(date_part, '%Y-%m-%d')
        except:
            timestamp = datetime.now()
        
        return NoteMetadata(
            filepath=path,
            timestamp=timestamp,
            topic=topic
        )
    
    def show_duplicate_comparison(self, match: DuplicateMatch) -> str:
        """Generate a visual comparison of duplicates"""
        output = []
        output.append("=" * 80)
        output.append(f"DUPLICATE DETECTED - {match.match_type.upper()} SIMILARITY ({match.similarity_score:.0%})")
        output.append("=" * 80)
        output.append("")
        output.append(f"📄 Note A: {match.note1.filepath.name}")
        output.append(f"   Date: {match.note1.timestamp.strftime('%Y-%m-%d')}")
        output.append(f"   Topic: {match.note1.topic}")
        output.append("")
        output.append(f"📄 Note B: {match.note2.filepath.name}")
        output.append(f"   Date: {match.note2.timestamp.strftime('%Y-%m-%d')}")
        output.append(f"   Topic: {match.note2.topic}")
        output.append("")
        
        if match.matching_segments:
            output.append("🔗 Matching Content:")
            for i, segment in enumerate(match.matching_segments[:3], 1):
                output.append(f"   {i}. {segment[:100]}...")
            output.append("")
        
        return "\n".join(output)


def interactive_duplicate_resolution(match: DuplicateMatch) -> str:
    """
    Interactive prompt for resolving a duplicate
    
    Returns: 'merge', 'link', 'keep', 'skip', or 'view'
    """
    print(DuplicateDetector().show_duplicate_comparison(match))
    print("Options:")
    print("  [m] Merge - Combine into single note with versions")
    print("  [l] Link - Keep separate but cross-reference")
    print("  [k] Keep - Mark as intentional reinforcement")
    print("  [s] Skip - Don't include in this consolidation")
    print("  [v] View - Show full content comparison")
    print("  [a] Auto - Apply this choice to similar duplicates")
    print("")
    
    while True:
        choice = input("Your choice: ").strip().lower()
        if choice in ['m', 'l', 'k', 's', 'v', 'a']:
            action_map = {
                'm': 'merge',
                'l': 'link',
                'k': 'keep',
                's': 'skip',
                'v': 'view',
                'a': 'auto'
            }
            return action_map[choice]
        print("Invalid choice. Please enter m, l, k, s, v, or a.")
