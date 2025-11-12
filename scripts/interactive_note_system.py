#!/usr/bin/env python3
"""
Enhanced Interactive Note-taking System for Learning Mentor with LLM Integration

This system follows these steps:
1. Capture user input as-is in a file
2. Provide updates/comments for clarity and proper arrangement
3. Consolidate notes when user says 'done for the day'
"""

import os
import datetime
import re
import json
import argparse
from pathlib import Path
import sys
from pathlib import Path

# Add project root to path for config import
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import OPENAI_MODEL, ANTHROPIC_MODEL, OLLAMA_MODEL, GOOGLE_MODEL
from typing import Optional, Any
from utils.topic_selector import TopicSelector, smart_topic_selection
from utils.duplicate_detector import DuplicateDetector, interactive_duplicate_resolution

# Try to import API libraries, but don't require them
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai: Optional[Any] = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic: Optional[Any] = None

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama: Optional[Any] = None

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    genai: Optional[Any] = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests: Optional[Any] = None

from config import OPENAI_API_KEY, OPENAI_MODEL, USE_LOCAL_PROCESSING

class InteractiveNoteTakingSystem:
    def __init__(self, consolidation_only=False):
        self.project_dir = Path.home() / "Projects" / "notes"
        self.topics_dir = self.project_dir / "topics"
        self.current_session_notes = []
        self.session_date = datetime.date.today().strftime("%Y-%m-%d")
        self._pending_first_note = None  # Store first note from topic identification
        
        # Load the learning mentor agent configuration
        self.agent_prompt = self._load_agent_prompt()
        
        # Set up API if available
        self.setup_api()
        
        # Only ask for topic if not in consolidation-only mode
        if not consolidation_only:
            # Ask user for topic or identify automatically with LLM
            self.topic = self.identify_topic_from_user()
            self.notes_file = self.topics_dir / self.topic / f"{self.session_date}.md"
            self.comments_file = self.topics_dir / self.topic / f"comments_{self.session_date}.md"

            # Ensure directories exist
            (self.topics_dir / self.topic).mkdir(parents=True, exist_ok=True)

            print(f"Starting note-taking session for {self.session_date}")
            print(f"Notes will be saved to: {self.notes_file}")
        else:
            # Set default topic for consolidation modes that need it
            self.topic = None
            self.notes_file = None
            self.comments_file = None

    def _sanitize_topic(self, topic):
        """Internal method to sanitize topic names"""
        from utils.file_operations import sanitize_topic_name
        return sanitize_topic_name(topic)
    
    def _load_agent_prompt(self):
        """Load the learning mentor agent configuration as the system prompt"""
        agent_file = self.project_dir / ".qwen" / "agents" / "learning-mentor.md"
        try:
            if agent_file.exists():
                with open(agent_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                # Fallback prompt if agent file not found
                return """You are a learning mentor AI assistant. Help users learn effectively by:
                - Providing clear, structured explanations
                - Suggesting related topics and resources
                - Encouraging deep understanding through questions
                - Adapting to the user's level of knowledge"""
        except Exception as e:
            print(f"Warning: Could not load agent prompt: {e}")
            return "You are a helpful learning mentor AI assistant."
        
    def setup_api(self):
        """Set up API clients if available"""
        # Set up OpenAI API
        if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            self.use_openai = True
        else:
            self.use_openai = False

        # Set up Anthropic API
        if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
            self.client_anthropic = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            self.use_anthropic = True
        else:
            self.use_anthropic = False

        # Set up Ollama
        self.use_ollama = OLLAMA_AVAILABLE
        
        # Set up Google API
        if GOOGLE_AVAILABLE and os.environ.get("GOOGLE_API_KEY"):
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            self.use_google = True
        else:
            self.use_google = False

        # Determine the primary LLM to use
        default_provider = os.environ.get("DEFAULT_LLM_PROVIDER", "openai")
        
        # Check if the default provider is available
        if default_provider == "openai" and self.use_openai:
            self.primary_llm = "openai"
        elif default_provider == "anthropic" and self.use_anthropic:
            self.primary_llm = "anthropic"
        elif default_provider == "ollama" and self.use_ollama:
            self.primary_llm = "ollama"
        elif default_provider == "google" and self.use_google:
            self.primary_llm = "google"
        elif self.use_openai:
            self.primary_llm = "openai"
        elif self.use_anthropic:
            self.primary_llm = "anthropic"
        elif self.use_ollama:
            self.primary_llm = "ollama"
        elif self.use_google:
            self.primary_llm = "google"
        else:
            self.primary_llm = None

    def call_llm(self, messages, max_tokens=None, temperature=0.7, provider=None):
        """
        Generic method to call any available LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate (None for unlimited/model default)
            temperature: Temperature for generation
            provider: Specific provider to use (openai, anthropic, ollama, google). If None, uses primary
        
        Returns:
            Generated text response from the LLM
        """
        # Determine which provider to use
        if provider is None:
            provider = self.primary_llm
            
        # If no provider is available, or if the requested provider is not available, return None
        if provider is None:
            return None
            
        try:
            if provider == "openai" and self.use_openai:
                # Use OpenAI with new API syntax
                from config import OPENAI_MODEL
                kwargs = {
                    "model": OPENAI_MODEL,
                    "messages": messages
                }
                
                # Only add temperature for models that support it
                # gpt-5-nano and some other models don't support temperature parameter
                if "gpt-5" not in OPENAI_MODEL.lower():
                    kwargs["temperature"] = temperature
                
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                    
                response = openai.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            elif provider == "anthropic" and self.use_anthropic:
                # Use Anthropic
                from config import ANTHROPIC_MODEL
                system_message = ""
                user_messages = []
                
                # Separate system message from user/assistant messages
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        user_messages.append(msg)
                
                kwargs = {
                    "model": ANTHROPIC_MODEL,
                    "system": system_message,
                    "messages": user_messages,
                    "temperature": temperature
                }
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                else:
                    kwargs["max_tokens"] = 4096  # Anthropic requires max_tokens
                
                response = self.client_anthropic.messages.create(**kwargs)
                return response.content[0].text
            elif provider == "ollama" and self.use_ollama:
                # Use Ollama
                from config import OLLAMA_MODEL
                # Combine messages into a single prompt for Ollama
                prompt = ""
                for msg in messages:
                    role = msg["role"]
                    content = msg["content"]
                    prompt += f"{role}: {content}\n"
                
                response = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response['message']['content']
            elif provider == "google" and self.use_google:
                # Use Google Generative AI
                from config import GOOGLE_MODEL
                import google.generativeai as genai
                
                # Combine messages into a single prompt for Gemini
                prompt = ""
                for msg in messages:
                    role = msg["role"]
                    content = msg["content"]
                    prompt += f"{role}: {content}\n"
                
                model = genai.GenerativeModel(GOOGLE_MODEL)
                
                kwargs = {
                    "temperature": temperature
                }
                if max_tokens is not None:
                    kwargs["max_output_tokens"] = max_tokens
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(**kwargs)
                )
                return response.text
            else:
                # Fallback to local logic if no provider is available
                return None
        except Exception as e:
            print(f"Error calling {provider} API: {e}")
            return None

    
    def identify_topic_from_user(self):
        """Prompt user to specify or identify a topic for the session"""
        print("\nWhat topic would you like to focus on today?")
        
        # Show existing topics if any
        existing_topics = self.list_existing_topics()
        if existing_topics:
            print(f"Existing topics: {', '.join(existing_topics)}")
        
        print("Examples: 'machine-learning', 'web-development', 'programming', 'data-science'")
        topic = input("Enter topic (or press Enter for automatic detection): ").strip()
        
        if not topic:
            # Automatically detect topic based on content with LLM assistance
            return self.identify_topic_with_llm()
        
        # Sanitize topic name (convert to lowercase, replace spaces with hyphens)
        topic = self._sanitize_topic(topic)
        return topic
    
    def identify_topic_with_llm(self):
        """Use local logic or LLM to identify topic from user's first note"""
        print("\nI'll help you identify the topic of your notes.")
        print("Enter your first note (this will help determine the topic):")
        
        first_note = input("First note: ").strip()
        
        if not first_note:
            print("No note provided, defaulting to 'general' topic.")
            return 'general'
        
        if self.primary_llm:
            # Use LLM for topic classification
            topic = self.classify_topic_with_llm(first_note)
        else:
            # Use local classification logic
            topic = self.classify_topic_with_local_logic(first_note)
        
        print(f"Based on your note, I've identified the topic as: '{topic}'")
        
        # Important: We store the first note for later capture in main() loop
        # This prevents duplicate capture
        self._pending_first_note = first_note
        
        return topic

    def get_topic_guidance(self, topic, user_query):
        """Get guidance on a specific topic from the LLM"""
        if not self.primary_llm:
            return "No LLM provider is configured."
        
        messages = [
            {"role": "system", "content": self.agent_prompt},
            {"role": "user", "content": f"Topic: {topic}\n\nQuery: {user_query}"}
        ]
        
        response = self.call_llm(messages=messages, temperature=0.7)
        
        if response:
            return response
        else:
            return f"Could not get guidance for topic '{topic}'. Please check your API configuration."
    
    def list_existing_topics(self):
        """List all existing topic directories"""
        try:
            if self.topics_dir.exists():
                return sorted([d.name for d in self.topics_dir.iterdir() if d.is_dir()])
            return []
        except Exception as e:
            print(f"❌ Error listing topics: {e}")
            return []
    
    def classify_topic_with_llm(self, note_content):
        """Use any available LLM to classify topic"""
        if not self.primary_llm:
            return self.classify_topic_with_local_logic(note_content)
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following note content, suggest a concise topic name (1-3 words) 
that best categorizes this learning material. The topic should be descriptive and suitable for organizing educational notes.

Respond with ONLY the topic name in lowercase with hyphens (e.g., 'machine-learning', 'quantum-physics', 'creative-writing').

Note content: {note_content}"""}
            ],
            temperature=0.3  # Lower temperature for more consistent topic naming
        )
        
        if response:
            topic = self._sanitize_topic(response)
            return topic if topic else 'general'
        
        # Fallback to local logic if LLM fails
        return self.classify_topic_with_local_logic(note_content)
    
    def classify_topic_with_local_logic(self, note_content):
        """Enhanced topic classification using more sophisticated local logic"""
        note_lower = note_content.lower()
        
        # More comprehensive topic mapping
        topic_keywords = {
            'programming': [
                'code', 'programming', 'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust',
                'function', 'class', 'method', 'variable', 'algorithm', 'debug', 'compile', 'syntax',
                'framework', 'library', 'api', 'database', 'sql', 'git', 'version control'
            ],
            'machine-learning': [
                'machine learning', 'ai', 'artificial intelligence', 'neural', 'model', 'data', 'algorithm',
                'training', 'prediction', 'classification', 'regression', 'tensorflow', 'pytorch', 'deep learning',
                'supervised', 'unsupervised', 'reinforcement learning', 'nlp', 'computer vision', 'feature', 'dataset'
            ],
            'web-development': [
                'web', 'html', 'css', 'javascript', 'react', 'vue', 'angular', 'frontend', 'backend',
                'api', 'rest', 'json', 'http', 'server', 'client', 'framework', 'bootstrap', 'node.js',
                'express', 'database', 'mysql', 'mongodb', 'responsive', 'ui', 'ux'
            ],
            'data-science': [
                'data', 'analysis', 'statistics', 'pandas', 'numpy', 'visualization', 'dataset', 'excel',
                'tableau', 'power bi', 'r', 'analytics', 'dashboard', 'correlation', 'regression', 'hypothesis',
                'experiment', 'sql', 'big data', 'business intelligence'
            ],
            'mathematics': [
                'math', 'equation', 'calculus', 'algebra', 'geometry', 'statistics', 'probability', 'trigonometry',
                'derivative', 'integral', 'function', 'theorem', 'proof', 'formula', 'variable', 'graph'
            ],
            'design': [
                'design', 'ui', 'ux', 'figma', 'photoshop', 'interface', 'user experience', 'wireframe',
                'prototype', 'mockup', 'color', 'typography', 'layout', 'user research', 'persona', 'user journey'
            ],
            'business': [
                'business', 'marketing', 'sales', 'finance', 'economics', 'strategy', 'management', 'leadership',
                'meeting', 'presentation', 'revenue', 'profit', 'cost', 'budget', 'investment', 'startup'
            ],
            'science': [
                'science', 'physics', 'chemistry', 'biology', 'research', 'experiment', 'hypothesis', 'lab',
                'molecule', 'atom', 'cell', 'organism', 'evolution', 'reaction', 'energy', 'force'
            ],
            'language': [
                'language', 'linguistics', 'vocabulary', 'grammar', 'syntax', 'translation', 'conversation',
                'pronunciation', 'writing', 'reading', 'speaking', 'fluency', 'idiom', 'phrase'
            ],
            'health': [
                'health', 'medicine', 'exercise', 'nutrition', 'diet', 'wellness', 'fitness', 'mental health',
                'symptom', 'treatment', 'therapy', 'meditation', 'sleep', 'stress', 'vitamin', 'disease'
            ]
        }
        
        # Score each topic based on keyword matches
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in note_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # If we found matching topics, return the one with the highest score
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        # If no keywords match, try to infer from context
        general_indicators = [
            ('general', ['general', 'overview', 'introduction']),
            ('study', ['study', 'learning', 'education', 'course', 'lesson', 'class', 'student']),
            ('project', ['project', 'task', 'work', 'goal', 'objective', 'plan'])
        ]
        
        for topic, indicators in general_indicators:
            if any(indicator in note_lower for indicator in indicators):
                return topic
        
        # Default to 'general' if nothing else matches
        return 'general'

    def capture_notes(self, user_input, source=None):
        """
        Capture user input as-is in raw format with metadata
        
        Args:
            user_input: The note content from user
            source: Optional source identifier (e.g., "Course A", "Session 1")
        """
        try:
            # Generate timestamp for this specific note
            timestamp = datetime.datetime.now()
            timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
            
            # Create raw directory if it doesn't exist
            raw_dir = self.topics_dir / self.topic / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            # File paths
            note_file = raw_dir / f"{timestamp_str}.md"
            metadata_file = raw_dir / f"{timestamp_str}.json"
            
            # Save raw note content
            with open(note_file, "w", encoding="utf-8") as f:
                f.write(user_input)
            
            # Create and save metadata
            metadata = {
                "topic": self.topic,
                "timestamp": timestamp.isoformat(),
                "capture_date": self.session_date,
                "source": source or "interactive_session",
                "session_id": f"{self.topic}_{self.session_date}",
                "tags": [],
                "note_count_in_session": len(self.current_session_notes) + 1
            }
            
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            
            # Also append to session file for backwards compatibility
            if self.notes_file:
                with open(self.notes_file, "a", encoding="utf-8") as f:
                    f.write(f"{user_input}\n")
            
            self.current_session_notes.append({
                'content': user_input,
                'timestamp': timestamp_str,
                'file': str(note_file)
            })
            
            print(f"✓ Note captured: {user_input[:50]}... → raw/{timestamp_str}.md")
        except IOError as e:
            print(f"❌ Error saving notes: {e}")
        except Exception as e:
            print(f"❌ Unexpected error while capturing notes: {e}")

    def add_comments_for_clarity(self, comments):
        """Add comments to provide clarity and proper arrangement"""
        try:
            with open(self.comments_file, "a", encoding="utf-8") as f:
                f.write(f"{comments}\n")
            print(f"✓ Comments added: {comments[:50]}...")
        except IOError as e:
            print(f"❌ Error saving comments: {e}")
        except Exception as e:
            print(f"❌ Unexpected error while adding comments: {e}")

    def get_current_notes(self):
        """Get the current notes content"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    return f.read()
            except IOError as e:
                print(f"❌ Error reading notes: {e}")
                return ""
        return ""

    def consolidate_notes(self, mode="topic-dates"):
        """
        Consolidate notes into a comprehensive learning guide with enhanced features
        
        Modes:
        - 'topic-dates': One topic, all its dates (default, current behavior)
        - 'date-topics': One date, all topics from that date  
        - 'all': All topics, all dates (comprehensive book)
        - 'topic-range': One topic, date range
        - 'date-range': Date range, all topics
        """
        if mode == "topic-dates":
            return self._consolidate_topic_all_dates()
        elif mode == "date-topics":
            return self._consolidate_date_all_topics(self.session_date)
        elif mode == "all":
            return self._consolidate_all_topics_all_dates()
        elif mode.startswith("topic-range"):
            # Will accept format: "topic-range:2024-01-01:2024-01-31"
            return self._consolidate_topic_date_range()
        elif mode.startswith("date-range"):
            # Will accept format: "date-range:2024-01-01:2024-01-31"
            return self._consolidate_date_range_all_topics()
        else:
            print(f"Unknown consolidation mode: {mode}. Using default 'topic-dates'")
            return self._consolidate_topic_all_dates()
    
    def _get_preview_statistics(self, topics=None, from_date=None, to_date=None):
        """Collect statistics for preview mode"""
        stats = {
            'total_notes': 0,
            'topics': {},
            'date_range': {'earliest': None, 'latest': None},
            'sources': set()
        }
        
        topics_to_scan = []
        if topics:
            topics_to_scan = [self.topics_dir / topic for topic in topics if (self.topics_dir / topic).exists()]
        else:
            topics_to_scan = [d for d in self.topics_dir.iterdir() if d.is_dir()]
        
        for topic_dir in topics_to_scan:
            topic_name = topic_dir.name
            note_count = 0
            
            # Check raw/ directory
            raw_dir = topic_dir / "raw"
            if raw_dir.exists():
                for note_file in raw_dir.glob("*.md"):
                    metadata_file = note_file.with_suffix('.json')
                    metadata = {}
                    
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                        except (IOError, json.JSONDecodeError):
                            pass
                    
                    note_date = metadata.get('capture_date', note_file.stem.split('_')[0])
                    
                    # Apply date filtering
                    if from_date and note_date < from_date:
                        continue
                    if to_date and note_date > to_date:
                        continue
                    
                    note_count += 1
                    source = metadata.get('source', 'interactive_session')
                    if source != 'interactive_session':
                        stats['sources'].add(source)
                    
                    # Update date range
                    if stats['date_range']['earliest'] is None or note_date < stats['date_range']['earliest']:
                        stats['date_range']['earliest'] = note_date
                    if stats['date_range']['latest'] is None or note_date > stats['date_range']['latest']:
                        stats['date_range']['latest'] = note_date
            else:
                # Old structure
                for date_file in topic_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"):
                    note_date = date_file.stem
                    
                    if from_date and note_date < from_date:
                        continue
                    if to_date and note_date > to_date:
                        continue
                    
                    note_count += 1
                    
                    if stats['date_range']['earliest'] is None or note_date < stats['date_range']['earliest']:
                        stats['date_range']['earliest'] = note_date
                    if stats['date_range']['latest'] is None or note_date > stats['date_range']['latest']:
                        stats['date_range']['latest'] = note_date
            
            if note_count > 0:
                stats['topics'][topic_name] = note_count
                stats['total_notes'] += note_count
        
        return stats

    def _consolidate_topic_all_dates(self, from_date=None, to_date=None, detect_duplicates=False, 
                                      duplicate_threshold=0.7, duplicate_strategy='prompt'):
        """Original behavior: Consolidate all notes from current topic across all dates"""
        # Collect all notes for this topic
        topic_dir = self.topics_dir / self.topic
        if not topic_dir.exists():
            print(f"No notes found for topic: {self.topic}")
            return None
        
        # Check for raw notes first (new structure)
        raw_dir = topic_dir / "raw"
        all_notes = []
        note_metadata = []
        
        if raw_dir.exists():
            # New structure: read from raw/ directory
            raw_files = sorted(raw_dir.glob("*.md"))
            
            for note_file in raw_files:
                # Load metadata
                metadata_file = note_file.with_suffix('.json')
                metadata = {}
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except (IOError, json.JSONDecodeError) as e:
                        print(f"⚠️  Warning: Could not load metadata for {note_file.name}: {e}")
                
                # Apply date filtering
                if from_date or to_date:
                    note_date = metadata.get('capture_date', note_file.stem.split('_')[0])
                    if from_date and note_date < from_date:
                        continue
                    if to_date and note_date > to_date:
                        continue
                
                # Read note content
                try:
                    with open(note_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            timestamp = metadata.get('timestamp', note_file.stem)
                            capture_date = metadata.get('capture_date', note_file.stem.split('_')[0])
                            source = metadata.get('source', 'interactive_session')
                            
                            note_header = f"### Notes from {capture_date}"
                            if timestamp and '_' in note_file.stem:
                                time_part = note_file.stem.split('_')[1]
                                note_header += f" ({time_part.replace('-', ':')})"
                            if source != 'interactive_session':
                                note_header += f" - *Source: {source}*"
                            note_header += f"\n*[View Raw Note]({note_file.name})*"
                            
                            all_notes.append(f"{note_header}\n\n{content}")
                            note_metadata.append({
                                'file': note_file,
                                'content': content,
                                'metadata': metadata,
                                'date': capture_date
                            })
                except IOError as e:
                    print(f"❌ Error reading {note_file}: {e}")
        else:
            # Fallback: old structure with YYYY-MM-DD.md files
            date_files = sorted(topic_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
            
            for note_file in date_files:
                date_str = note_file.stem
                
                # Apply date filtering
                if from_date and date_str < from_date:
                    continue
                if to_date and date_str > to_date:
                    continue
                
                try:
                    with open(note_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            all_notes.append(f"### Notes from {date_str}\n\n{content}")
                            note_metadata.append({
                                'file': note_file,
                                'content': content,
                                'metadata': {'capture_date': date_str},
                                'date': date_str
                            })
                except IOError as e:
                    print(f"❌ Error reading {note_file}: {e}")
        
        if not all_notes:
            print("No notes found to consolidate.")
            return None
        
        # Duplicate detection
        if detect_duplicates and len(note_metadata) > 1:
            print(f"\n🔍 Checking for duplicate content (threshold: {duplicate_threshold})...")
            detector = DuplicateDetector(threshold=duplicate_threshold)
            
            duplicates = detector.find_duplicates([nm['content'] for nm in note_metadata])
            
            if duplicates:
                print(f"Found {len(duplicates)} potential duplicate(s)")
                
                if duplicate_strategy == 'prompt':
                    # Interactive resolution
                    for dup in duplicates:
                        note1_info = note_metadata[dup.index1]
                        note2_info = note_metadata[dup.index2]
                        
                        result = interactive_duplicate_resolution(
                            dup.content1, dup.content2,
                            note1_info['metadata'], note2_info['metadata'],
                            dup.similarity
                        )
                        
                        if result['action'] == 'merge':
                            # Merge notes
                            merged_content = result.get('merged_content', dup.content1 + "\n\n" + dup.content2)
                            all_notes[dup.index1] = f"### Merged Notes\n\n{merged_content}"
                            all_notes[dup.index2] = ""  # Remove duplicate
                        elif result['action'] == 'link':
                            # Add cross-references
                            all_notes[dup.index1] += f"\n\n*See also: Notes from {note2_info['date']}*"
                            all_notes[dup.index2] += f"\n\n*See also: Notes from {note1_info['date']}*"
                        # 'keep' and 'skip' don't modify notes
                
                elif duplicate_strategy == 'merge':
                    # Auto-merge high similarity (>90%)
                    for dup in duplicates:
                        if dup.similarity > 0.9:
                            merged_content = dup.content1 + "\n\n---\n\n" + dup.content2
                            all_notes[dup.index1] = f"### Merged Notes\n\n{merged_content}"
                            all_notes[dup.index2] = ""
                
                elif duplicate_strategy == 'link':
                    # Auto-link all duplicates
                    for dup in duplicates:
                        note1_info = note_metadata[dup.index1]
                        note2_info = note_metadata[dup.index2]
                        all_notes[dup.index1] += f"\n\n*Related: Notes from {note2_info['date']}*"
                        all_notes[dup.index2] += f"\n\n*Related: Notes from {note1_info['date']}*"
                
                # 'keep' strategy: do nothing, keep all duplicates
                
                # Remove empty notes (from merges)
                all_notes = [note for note in all_notes if note.strip()]
            
        original_notes = "\n\n---\n\n".join(all_notes)

        print("🔄 Generating comprehensive learning guide...")
        
        # Create a consolidated guide
        guide_filename = self.topics_dir / self.topic / f"learning-guide.md"

        # Start building the guide
        guide_content = f"""# Learning Guide: {self.topic.replace('-', ' ').title()}
*Session Date: {self.session_date}*

---

"""

        # Generate and add TL;DR summary
        if self.primary_llm:
            print("  📝 Generating summary...")
            summary = self.generate_summary(original_notes)
            if summary:
                guide_content += f"""## 📋 TL;DR Summary

{summary}

---

"""

        # Add original notes
        guide_content += f"""## 📖 Original Notes

{original_notes}

---

"""

        # Add comments if any
        guide_content += "## 💭 Comments for Clarity\n\n"
        if self.comments_file and self.comments_file.exists():
            try:
                with open(self.comments_file, "r", encoding="utf-8") as f:
                    comments = f.read()
                guide_content += f"{comments}\n"
            except IOError as e:
                print(f"❌ Error reading comments: {e}")
                guide_content += "Error reading comments.\n"
        else:
            guide_content += "No additional comments provided.\n"
        
        guide_content += "\n---\n\n"

        # Generate auto-tags
        if self.primary_llm:
            print("  🏷️  Generating tags...")
            tags = self.generate_auto_tags(original_notes)
            if tags:
                guide_content += f"""## 🏷️ Key Concepts & Tags

{', '.join([f'`{tag}`' for tag in tags])}

---

"""

        # Generate visual diagram
        if self.primary_llm:
            print("  📊 Creating visual diagram...")
            diagram = self.generate_mermaid_diagram(original_notes)
            if diagram:
                guide_content += f"""## 📊 Visual Concept Map

```mermaid
{diagram}
```

---

"""

        # Generate concept links
        if self.primary_llm:
            print("  🔗 Finding concept connections...")
            concept_links = self.find_concept_links(original_notes)
            if concept_links:
                guide_content += f"""## 🔗 Related Concepts to Explore

{concept_links}

---

"""

        # Generate quiz questions
        if self.primary_llm:
            print("  ❓ Creating review questions...")
            quiz = self.generate_quiz_questions(original_notes)
            if quiz:
                guide_content += f"""## ❓ Review Questions (Active Recall)

{quiz}

---

"""

        # Generate flashcards
        if self.primary_llm:
            print("  🗂️  Creating flashcards...")
            flashcards = self.generate_flashcards(original_notes)
            if flashcards:
                guide_content += f"""## 🗂️ Flashcards for Spaced Repetition

{flashcards}

---

"""

        # Generate citations and resources
        if self.primary_llm:
            print("  📚 Finding learning resources...")
            citations = self.generate_citations(original_notes)
            if citations:
                guide_content += f"""## 📚 Recommended Resources

{citations}

---

"""

        # Generate additional structured content
        if self.primary_llm:
            print("  ✨ Generating additional insights...")
            additional_content = self.generate_additional_content_with_llm(original_notes)
            guide_content += additional_content
        else:
            guide_content += self.get_default_additional_content()

        # Add footer with metadata
        guide_content += f"""
---

*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Topic: {self.topic}*  
*Learning Mentor AI System*
"""

        # Save the guide
        try:
            with open(guide_filename, "w", encoding="utf-8") as f:
                f.write(guide_content)
        except IOError as e:
            print(f"❌ Error saving consolidated notes: {e}")
            return None

        print(f"✅ Comprehensive learning guide created: {guide_filename}")
        return guide_filename
    
    def generate_additional_content_with_llm(self, original_notes):
        """Generate additional educational content using LLM"""
        additional_content = "\n"
        
        if self.primary_llm and original_notes.strip():
            response = self.call_llm(
                messages=[
                    {"role": "system", "content": self.agent_prompt},
                    {"role": "user", "content": f"""Based on the notes provided below, generate a structured learning guide with the following sections:
1. Related Topics to Explore
2. Additional Resources (articles, books, videos, or courses)
3. Key Takeaways (summarized key points)
4. Next Steps (actionable items to continue learning)

Format your response in markdown with clear sections.

Notes:
{original_notes}"""}
                ],
                temperature=0.7
            )
            
            if response:
                additional_content += response
            else:
                print("LLM unavailable, using template instead.")
                additional_content += self.get_default_additional_content()
        else:
            additional_content += self.get_default_additional_content()
        
        return additional_content
    
    def generate_auto_tags(self, notes_content):
        """Extract key concepts and tags from notes"""
        if not self.primary_llm or not notes_content.strip():
            return []
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Analyze the following notes and extract 5-10 key concepts or tags that represent the main ideas.
Return them as a comma-separated list (e.g., "neural networks, backpropagation, gradient descent").

Notes:
{notes_content}"""}
            ],
            temperature=0.3
        )
        
        if response:
            # Parse comma-separated tags
            tags = [tag.strip().lower() for tag in response.split(',')]
            return [tag for tag in tags if tag]
        return []
    
    def generate_mermaid_diagram(self, notes_content):
        """Generate a Mermaid diagram (concept map or flowchart) from notes"""
        if not self.primary_llm or not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following notes, create a visual representation using Mermaid syntax.
Choose the most appropriate diagram type:
- Use a mindmap for concept hierarchies
- Use a flowchart for processes or workflows
- Use a graph for relationships between concepts

Return ONLY valid Mermaid syntax, no explanation.

Notes:
{notes_content}"""}
            ],
            temperature=0.5
        )
        
        return response if response else None
    
    def generate_quiz_questions(self, notes_content):
        """Generate review questions for active recall"""
        if not self.primary_llm or not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following notes, generate 5-7 thought-provoking questions that would help someone review and test their understanding.
Include a mix of:
- Recall questions (what, when, who)
- Comprehension questions (explain, describe)
- Application questions (how would you use this)

Format as a numbered list.

Notes:
{notes_content}"""}
            ],
            temperature=0.7
        )
        
        return response if response else None
    
    def generate_flashcards(self, notes_content):
        """Generate flashcards in Anki-compatible format"""
        if not self.primary_llm or not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following notes, create 8-10 flashcards for spaced repetition learning.
Format each flashcard as:
**Q:** [Question]
**A:** [Answer]

Focus on key concepts, definitions, and important facts.

Notes:
{notes_content}"""}
            ],
            temperature=0.6
        )
        
        return response if response else None
    
    def generate_summary(self, notes_content):
        """Generate a concise TL;DR summary"""
        if not self.primary_llm or not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Create a concise TL;DR (Too Long; Didn't Read) summary of the following notes in 3-5 bullet points.
Capture only the most essential information.

Notes:
{notes_content}"""}
            ],
            temperature=0.5
        )
        
        return response if response else None
    
    def find_concept_links(self, notes_content):
        """Identify related concepts that connect to other topics"""
        if not self.primary_llm or not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Analyze the following notes and identify 3-5 related concepts or topics that the learner should explore to deepen their understanding.
For each, briefly explain (1 sentence) why it's relevant.

Format as:
- **[Concept]**: [Why it's relevant]

Notes:
{notes_content}"""}
            ],
            temperature=0.7
        )
        
        return response if response else None
    
    def generate_citations(self, notes_content):
        """Suggest relevant academic resources and citations"""
        if not self.primary_llm or not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following notes, suggest 3-5 high-quality learning resources:
- Academic papers or books
- Online courses
- Video tutorials
- Documentation or tutorials

Format as a list with brief descriptions.

Notes:
{notes_content}"""}
            ],
            temperature=0.6
        )
        
        return response if response else None

    def get_default_additional_content(self):
        """Get default additional content when API is not available"""
        return """
## Related Topics to Explore
- [Based on the topics covered in your notes]

## Additional Resources
- [Relevant articles, books, videos, or courses]

## Key Takeaways
- [Summarized key points from your learning session]

## Next Steps
- [Actionable items to continue your learning journey]

"""

    def _consolidate_date_all_topics(self, target_date=None, from_date=None, to_date=None):
        """Consolidate all topics from a specific date into daily summary"""
        if target_date is None:
            target_date = self.session_date
            
        print(f"🔄 Creating daily summary for {target_date}...")
        
        # Find all topics that have notes for this date
        all_notes_by_topic = {}
        
        for topic_dir in self.topics_dir.iterdir():
            if topic_dir.is_dir():
                topic_name = topic_dir.name
                
                # Try raw/ directory first (new structure)
                raw_dir = topic_dir / "raw"
                if raw_dir.exists():
                    for note_file in raw_dir.glob("*.md"):
                        metadata_file = note_file.with_suffix('.json')
                        metadata = {}
                        
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                            except (IOError, json.JSONDecodeError):
                                pass
                        
                        # Get date from metadata or filename
                        note_date = metadata.get('capture_date', note_file.stem.split('_')[0])
                        
                        # Check if note matches target date
                        if note_date == target_date:
                            try:
                                with open(note_file, "r", encoding="utf-8") as f:
                                    content = f.read().strip()
                                    if content:
                                        if topic_name not in all_notes_by_topic:
                                            all_notes_by_topic[topic_name] = []
                                        
                                        timestamp = note_file.stem.split('_')[1] if '_' in note_file.stem else ''
                                        source = metadata.get('source', 'interactive_session')
                                        
                                        note_header = ""
                                        if timestamp:
                                            note_header += f"*Time: {timestamp.replace('-', ':')}*"
                                        if source != 'interactive_session':
                                            note_header += f" - *Source: {source}*"
                                        if note_header:
                                            note_header += "\n\n"
                                        
                                        all_notes_by_topic[topic_name].append(note_header + content)
                            except IOError as e:
                                print(f"❌ Error reading {note_file}: {e}")
                else:
                    # Fallback to old structure
                    date_file = topic_dir / f"{target_date}.md"
                    if date_file.exists():
                        try:
                            with open(date_file, "r", encoding="utf-8") as f:
                                content = f.read().strip()
                                if content:
                                    all_notes_by_topic[topic_name] = [content]
                        except IOError as e:
                            print(f"❌ Error reading {date_file}: {e}")
        
        if not all_notes_by_topic:
            print(f"No notes found for date: {target_date}")
            return None
        
        # Merge multiple notes per topic
        for topic in all_notes_by_topic:
            if isinstance(all_notes_by_topic[topic], list):
                all_notes_by_topic[topic] = "\n\n---\n\n".join(all_notes_by_topic[topic])
        
        # Build consolidated content
        guide_content = f"""# Daily Learning Summary
*Date: {target_date}*
*Topics covered: {len(all_notes_by_topic)}*

---

"""
        
        original_notes_section = "## 📖 Notes by Topic\n\n"
        for topic, content in sorted(all_notes_by_topic.items()):
            original_notes_section += f"""### {topic.replace('-', ' ').title()}

{content}

---

"""
        
        guide_content += original_notes_section
        
        # Combine all notes for LLM processing
        combined_notes = "\n\n".join([
            f"**{topic.replace('-', ' ').title()}**:\n{content}" 
            for topic, content in all_notes_by_topic.items()
        ])
        
        # Generate insights across all topics
        if self.primary_llm:
            print("  ✨ Generating cross-topic insights...")
            daily_insights = self.call_llm(
                prompt=f"""Analyze this day's learning across multiple topics and provide:
1. Common themes or connections between topics
2. Overall learning progress assessment
3. Suggested focus areas for tomorrow

Notes from {target_date}:
{combined_notes}""",
                system_message=self.agent_prompt
            )
            
            if daily_insights:
                guide_content += f"""## 🧠 Daily Insights

{daily_insights}

---

"""
        
        # Save daily summary
        daily_dir = self.project_dir / "daily_notes"
        daily_dir.mkdir(exist_ok=True)
        guide_filename = daily_dir / f"daily-summary-{target_date}.md"
        
        guide_content += f"""
---

*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Daily Summary for {target_date}*  
*Learning Mentor AI System*
"""
        
        try:
            with open(guide_filename, "w", encoding="utf-8") as f:
                f.write(guide_content)
            print(f"✅ Daily summary created: {guide_filename}")
            return guide_filename
        except IOError as e:
            print(f"❌ Error saving daily summary: {e}")
            return None
    
    def _consolidate_all_topics_all_dates(self, from_date=None, to_date=None, topics_filter=None, 
                                           detect_duplicates=False, duplicate_threshold=0.7, 
                                           duplicate_strategy='prompt'):
        """Create comprehensive book from all notes across all topics and dates"""
        print("📚 Creating comprehensive learning book from all notes...")
        print("   This may take a while for large collections...")
        
        # Collect all notes organized by topic
        all_topics = {}
        all_note_metadata = []
        
        for topic_dir in sorted(self.topics_dir.iterdir()):
            if topic_dir.is_dir():
                topic_name = topic_dir.name
                
                # Apply topic filter
                if topics_filter and topic_name not in topics_filter:
                    continue
                
                # Try raw/ directory first (new structure)
                raw_dir = topic_dir / "raw"
                if raw_dir.exists():
                    topic_notes = []
                    for note_file in sorted(raw_dir.glob("*.md")):
                        metadata_file = note_file.with_suffix('.json')
                        metadata = {}
                        
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                            except (IOError, json.JSONDecodeError):
                                pass
                        
                        # Get date from metadata or filename
                        note_date = metadata.get('capture_date', note_file.stem.split('_')[0])
                        
                        # Apply date filtering
                        if from_date and note_date < from_date:
                            continue
                        if to_date and note_date > to_date:
                            continue
                        
                        try:
                            with open(note_file, "r", encoding="utf-8") as f:
                                content = f.read().strip()
                                if content:
                                    timestamp = note_file.stem.split('_')[1] if '_' in note_file.stem else ''
                                    source = metadata.get('source', 'interactive_session')
                                    
                                    topic_notes.append({
                                        'date': note_date,
                                        'timestamp': timestamp,
                                        'source': source,
                                        'content': content,
                                        'file': note_file.name
                                    })
                                    
                                    all_note_metadata.append({
                                        'topic': topic_name,
                                        'content': content,
                                        'metadata': metadata
                                    })
                        except IOError as e:
                            print(f"❌ Error reading {note_file}: {e}")
                    
                    if topic_notes:
                        all_topics[topic_name] = topic_notes
                else:
                    # Fallback to old structure
                    date_files = sorted(topic_dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
                    topic_notes = []
                    
                    for date_file in date_files:
                        note_date = date_file.stem
                        
                        # Apply date filtering
                        if from_date and note_date < from_date:
                            continue
                        if to_date and note_date > to_date:
                            continue
                        
                        try:
                            with open(date_file, "r", encoding="utf-8") as f:
                                content = f.read().strip()
                                if content:
                                    topic_notes.append({
                                        'date': note_date,
                                        'timestamp': '',
                                        'source': 'interactive_session',
                                        'content': content,
                                        'file': date_file.name
                                    })
                                    
                                    all_note_metadata.append({
                                        'topic': topic_name,
                                        'content': content,
                                        'metadata': {'capture_date': note_date}
                                    })
                        except IOError as e:
                            print(f"❌ Error reading {date_file}: {e}")
                    
                    if topic_notes:
                        all_topics[topic_name] = topic_notes
        
        if not all_topics:
            print("No notes found to consolidate.")
            return None
        
        # Build comprehensive book
        total_notes = sum(len(notes) for notes in all_topics.values())
        book_content = f"""# Complete Learning Journey
*Comprehensive Guide Across All Topics*

**Statistics:**
- Topics covered: {len(all_topics)}
- Total sessions: {total_notes}
- Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 Table of Contents

"""
        
        # Add table of contents
        for idx, topic in enumerate(sorted(all_topics.keys()), 1):
            book_content += f"{idx}. [{topic.replace('-', ' ').title()}](#{topic})\n"
        
        book_content += "\n---\n\n"
        
        # Add each topic as a chapter
        for topic_name, topic_notes in sorted(all_topics.items()):
            chapter_content = f"""## {topic_name.replace('-', ' ').title()} {{#{topic_name}}}

*Sessions: {len(topic_notes)}*

"""
            
            # Add chronological notes
            for note in topic_notes:
                chapter_content += f"""### Session: {note['date']}

{note['content']}

---

"""
            
            # Generate chapter summary if LLM available
            if self.primary_llm:
                print(f"  📖 Summarizing {topic_name}...")
                combined_topic_notes = "\n\n".join([n['content'] for n in topic_notes])
                
                summary = self.call_llm(
                    prompt=f"""Create a comprehensive summary of this learning journey for the topic "{topic_name}".
Include:
1. Key concepts mastered
2. Learning progression over time
3. Important insights
4. Recommended next steps

Notes:
{combined_topic_notes}""",
                    system_message=self.agent_prompt
                )
                
                if summary:
                    chapter_content += f"""### 📋 Chapter Summary

{summary}

---

"""
            
            book_content += chapter_content + "\n\n"
        
        # Add comprehensive insights
        if self.primary_llm:
            print("  🎓 Generating overall learning insights...")
            
            # Create overview of all topics
            topics_overview = "\n".join([
                f"- {topic.replace('-', ' ').title()}: {len(notes)} sessions"
                for topic, notes in all_topics.items()
            ])
            
            overall_insights = self.call_llm(
                prompt=f"""Based on this complete learning journey across multiple topics, provide:
1. Overall learning achievements and growth
2. Connections between different topics
3. Knowledge gaps to fill
4. Recommended learning path forward
5. Areas of expertise developed

Topics covered:
{topics_overview}""",
                system_message=self.agent_prompt
            )
            
            if overall_insights:
                book_content += f"""## 🎓 Overall Learning Journey Insights

{overall_insights}

---

"""
        
        # Save the book
        book_filename = self.project_dir / "complete-learning-book.md"
        book_content += f"""
---

*Complete Learning Book*  
*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Learning Mentor AI System*
"""
        
        try:
            with open(book_filename, "w", encoding="utf-8") as f:
                f.write(book_content)
            print(f"✅ Complete learning book created: {book_filename}")
            print(f"   📊 {len(all_topics)} topics, {total_notes} sessions compiled")
            return book_filename
        except IOError as e:
            print(f"❌ Error saving learning book: {e}")
            return None

def main():
    """Main entry point with argument parsing for different consolidation modes"""
    parser = argparse.ArgumentParser(
        description="Learning Mentor Note-Taking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Consolidation Modes:
  topic-dates     - Consolidate one topic across all dates (default)
  date-topics     - Consolidate all topics from a specific date (daily summary)
  all             - Create comprehensive book from all topics and dates
  
Examples:
  # Interactive note-taking (default mode)
  python interactive_note_system.py
  
  # Interactive topic selection
  python interactive_note_system.py --select-topics
  
  # Fuzzy search and consolidate
  python interactive_note_system.py --topics web
  
  # Consolidate specific topics
  python interactive_note_system.py --topics pytorch,deep-learning
  
  # Create daily summary for date range
  python interactive_note_system.py --mode date-topics --from-date 2024-11-01 --to-date 2024-11-10
  
  # Generate book excluding basics topics
  python interactive_note_system.py --mode all --exclude-topics basics,intro
  
  # With duplicate detection
  python interactive_note_system.py --mode all --detect-duplicates --duplicate-threshold 0.8
        """
    )
    
    # Basic options
    parser.add_argument(
        '--consolidate',
        metavar='TOPIC',
        help='Consolidate notes for a specific topic'
    )
    
    parser.add_argument(
        '--mode',
        choices=['topic-dates', 'date-topics', 'all'],
        default='topic-dates',
        help='Consolidation mode (default: topic-dates)'
    )
    
    # Topic selection
    parser.add_argument(
        '--topics',
        metavar='TOPICS',
        help='Comma-separated topics or fuzzy search query (e.g., "web" or "pytorch,ml")'
    )
    
    parser.add_argument(
        '--exclude-topics',
        metavar='TOPICS',
        help='Comma-separated topics to exclude'
    )
    
    parser.add_argument(
        '--select-topics',
        action='store_true',
        help='Interactive topic selection with fuzzy matching'
    )
    
    # Date filtering
    parser.add_argument(
        '--date',
        metavar='YYYY-MM-DD',
        help='Specific date for date-topics mode'
    )
    
    parser.add_argument(
        '--from-date',
        metavar='YYYY-MM-DD',
        help='Start date for date range filtering'
    )
    
    parser.add_argument(
        '--to-date',
        metavar='YYYY-MM-DD',
        help='End date for date range filtering'
    )
    
    # Duplicate detection
    parser.add_argument(
        '--detect-duplicates',
        action='store_true',
        help='Enable duplicate detection'
    )
    
    parser.add_argument(
        '--duplicate-threshold',
        type=float,
        default=0.7,
        metavar='FLOAT',
        help='Similarity threshold for duplicates (0.0-1.0, default: 0.7)'
    )
    
    parser.add_argument(
        '--duplicate-strategy',
        choices=['prompt', 'merge', 'link', 'keep'],
        default='prompt',
        help='How to handle duplicates: prompt (ask), merge (auto-merge >90%%), link (cross-ref), keep (all)'
    )
    
    # Other options
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview what will be consolidated before generating'
    )
    
    parser.add_argument(
        '--source',
        metavar='NAME',
        help='Source identifier for notes (e.g., "Course A", "Book: Deep Learning")'
    )
    
    args = parser.parse_args()
    
    # Handle consolidation-only mode
    if args.consolidate or args.mode != 'topic-dates' or args.select_topics or args.topics:
        nts = InteractiveNoteTakingSystem(consolidation_only=True)
        
        # Topic selection
        selected_topics = []
        
        if args.select_topics:
            # Interactive selection
            selector = TopicSelector(nts.topics_dir)
            selected_topics = selector.interactive_select(mode="include", allow_multiple=True)
            
            if not selected_topics:
                print("No topics selected. Exiting.")
                return
        
        elif args.topics:
            # Parse topics (could be fuzzy search or comma-separated)
            if ',' in args.topics:
                # Comma-separated list
                selected_topics = [t.strip() for t in args.topics.split(',')]
            else:
                # Fuzzy search
                selector = TopicSelector(nts.topics_dir)
                matches = selector.fuzzy_match(args.topics)
                
                if not matches:
                    print(f"❌ No topics found matching '{args.topics}'")
                    return
                
                if len(matches) == 1:
                    selected_topics = [matches[0][0]]
                    print(f"✓ Found topic: {selected_topics[0]}")
                else:
                    print(f"\n🔍 Found {len(matches)} matching topics:")
                    for i, (topic, score, count, date_range) in enumerate(matches, 1):
                        print(f"  {i}. {topic} ({count} notes)")
                    
                    choice = input("\nSelect topic number (or 'all' for all matches): ").strip()
                    
                    if choice.lower() == 'all':
                        selected_topics = [topic for topic, _, _, _ in matches]
                    elif choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(matches):
                            selected_topics = [matches[idx][0]]
                    else:
                        print("Invalid selection")
                        return
        
        elif args.consolidate:
            selected_topics = [nts._sanitize_topic(args.consolidate)]
        
        # Exclude topics if specified
        excluded_topics = []
        if args.exclude_topics:
            excluded_topics = [t.strip() for t in args.exclude_topics.split(',')]
            selected_topics = [t for t in selected_topics if t not in excluded_topics]
        
        # Preview if requested
        if args.preview:
            print("\n🔍 Collecting statistics...")
            stats = nts._get_preview_statistics(
                topics=selected_topics if selected_topics else None,
                from_date=args.from_date,
                to_date=args.to_date
            )
            
            print("\n" + "=" * 80)
            print("CONSOLIDATION PREVIEW")
            print("=" * 80)
            print(f"Mode: {args.mode}")
            
            if stats['topics']:
                print(f"\nTopics ({len(stats['topics'])}):")
                for topic, count in sorted(stats['topics'].items()):
                    print(f"  • {topic}: {count} note(s)")
            else:
                print("\n⚠️  No notes found matching criteria")
                return
            
            print(f"\nTotal notes: {stats['total_notes']}")
            
            if stats['date_range']['earliest']:
                print(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
            
            if stats['sources']:
                print(f"Sources: {', '.join(sorted(stats['sources']))}")
            
            if args.detect_duplicates:
                print(f"\n🔍 Duplicate detection: ON (threshold: {args.duplicate_threshold}, strategy: {args.duplicate_strategy})")
            
            print("=" * 80)
            
            proceed = input("\nProceed with consolidation? [Y/n]: ").strip().lower()
            if proceed == 'n':
                print("Cancelled.")
                return
        
        # Execute consolidation based on mode
        if args.mode == 'date-topics':
            target_date = args.date if args.date else nts.session_date
            nts._consolidate_date_all_topics(
                target_date=target_date,
                from_date=args.from_date,
                to_date=args.to_date
            )
        
        elif args.mode == 'all':
            nts._consolidate_all_topics_all_dates(
                from_date=args.from_date,
                to_date=args.to_date,
                topics_filter=selected_topics if selected_topics else None,
                detect_duplicates=args.detect_duplicates,
                duplicate_threshold=args.duplicate_threshold,
                duplicate_strategy=args.duplicate_strategy
            )
        
        else:  # topic-dates
            if selected_topics:
                for topic in selected_topics:
                    nts.topic = topic
                    print(f"\n📚 Consolidating: {topic}")
                    nts._consolidate_topic_all_dates(
                        from_date=args.from_date,
                        to_date=args.to_date,
                        detect_duplicates=args.detect_duplicates,
                        duplicate_threshold=args.duplicate_threshold,
                        duplicate_strategy=args.duplicate_strategy
                    )
            else:
                print("Error: No topic specified. Use --topics, --select-topics, or --consolidate")
                parser.print_help()
                return
        
        return
    
    # Normal interactive mode
    nts = InteractiveNoteTakingSystem(consolidation_only=False)
    
    # Set source if provided
    note_source = args.source if args.source else None
    
    # Capture the pending first note if it exists (from topic identification)
    if nts._pending_first_note:
        nts.capture_notes(nts._pending_first_note, source=note_source)
        nts._pending_first_note = None

    print("\nLearning Mentor Note-Taking System")
    print("Type 'done for the day' when you've finished your session")
    print("Type 'add comment' to add comments for clarity")
    if note_source:
        print(f"Source: {note_source}")
    print("Type 'quit' to exit without consolidating")
    print("-" * 50)

    while True:
        user_input = input("\nEnter your notes or command: ").strip()

        if user_input.lower() == "done for the day":
            print("\nConsolidating your notes into a detailed guide...")
            
            # Detect duplicates if enabled
            if args.detect_duplicates:
                # TODO: Implement duplicate detection in consolidation
                print("🔍 Duplicate detection enabled...")
            
            nts.consolidate_notes()
            print("Thank you for your learning session! Your notes have been consolidated.")
            break
        elif user_input.lower() == "add comment":
            comment = input("Enter your comment for clarity: ").strip()
            if comment:
                nts.add_comments_for_clarity(comment)
        elif user_input.lower() == "quit":
            print("Exiting without consolidation.")
            break
        elif user_input:
            nts.capture_notes(user_input, source=note_source)
        else:
            print("Please enter some notes or a command.")

if __name__ == "__main__":
    main()