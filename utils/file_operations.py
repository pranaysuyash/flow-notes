"""
Utility functions for the Learning Mentor Note-Taking System
"""

import os
from pathlib import Path
import datetime
import re


def sanitize_topic_name(topic):
    """Sanitize topic name (convert to lowercase, replace spaces with hyphens)"""
    topic = re.sub(r'[^\w\s-]', '', topic).strip().lower().replace(' ', '-')
    return topic


def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.date.today().strftime("%Y-%m-%d")


def get_current_datetime():
    """Get current datetime in YYYY-MM-DD HH:MM:SS format"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_directory_exists(path):
    """Ensure a directory exists, creating it if necessary"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_to_file(file_path, content, mode="a", encoding="utf-8"):
    """Write content to a file with error handling"""
    try:
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"❌ Error writing to file {file_path}: {e}")
        return False


def read_from_file(file_path, encoding="utf-8"):
    """Read content from a file with error handling"""
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except IOError as e:
        print(f"❌ Error reading from file {file_path}: {e}")
        return ""


def file_exists(file_path):
    """Check if a file exists"""
    return Path(file_path).exists()


def list_directory_contents(directory_path):
    """List contents of a directory"""
    path = Path(directory_path)
    if path.exists() and path.is_dir():
        return [item.name for item in path.iterdir()]
    return []


def get_project_root():
    """Get the project root directory"""
    return Path.home() / "Projects" / "notes"


def get_topics_directory():
    """Get the topics directory"""
    project_root = get_project_root()
    topics_dir = project_root / "topics"
    ensure_directory_exists(topics_dir)
    return topics_dir


def get_daily_notes_directory():
    """Get the daily notes directory"""
    project_root = get_project_root()
    daily_notes_dir = project_root / "daily_notes"
    ensure_directory_exists(daily_notes_dir)
    return daily_notes_dir


def get_notes_file_path(topic, date=None):
    """Get the path for notes file"""
    if date is None:
        date = get_current_date()
    
    topics_dir = get_topics_directory()
    topic_dir = topics_dir / topic
    ensure_directory_exists(topic_dir)
    
    return topic_dir / f"{date}.md"


def get_comments_file_path(topic, date=None):
    """Get the path for comments file"""
    if date is None:
        date = get_current_date()
    
    topics_dir = get_topics_directory()
    topic_dir = topics_dir / topic
    ensure_directory_exists(topic_dir)
    
    return topic_dir / f"comments_{date}.md"


def get_consolidated_guide_path(topic, date=None):
    """Get the path for consolidated guide file"""
    if date is None:
        date = get_current_date()
    
    topics_dir = get_topics_directory()
    topic_dir = topics_dir / topic
    ensure_directory_exists(topic_dir)
    
    return topic_dir / f"consolidated_guide_{date}.md"


def get_daily_notes_file_path(topic, date=None):
    """Get the path for daily notes file"""
    if date is None:
        date = get_current_date()
    
    daily_notes_dir = get_daily_notes_directory()
    
    return daily_notes_dir / f"{date}_{topic}.md"


def get_daily_summary_path(topic, date=None):
    """Get the path for daily summary file"""
    if date is None:
        date = get_current_date()
    
    daily_notes_dir = get_daily_notes_directory()
    
    return daily_notes_dir / f"summary_{date}_{topic}.md"


def get_api_key(provider):
    """Get API key for a specific provider from environment"""
    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY", 
        "google": "GOOGLE_API_KEY",
        "ollama": "OLLAMA_HOST"  # Ollama uses host, not API key
    }
    
    env_var = env_var_map.get(provider.lower())
    if env_var:
        return os.getenv(env_var)
    return None


def is_provider_available(provider):
    """Check if a specific provider is available (has API key set)"""
    if provider.lower() == "ollama":
        # Ollama availability is based on host accessibility rather than API key
        return os.getenv("OLLAMA_HOST", "http://localhost:11434") is not None
    else:
        return bool(get_api_key(provider))


def create_init_files():
    """Create __init__.py files to make directories into Python packages"""
    init_files = [
        "utils/__init__.py",
        "tests/__init__.py", 
        "scripts/__init__.py",
        "docs/__init__.py"
    ]
    
    for init_file in init_files:
        file_path = Path(init_file)
        if not file_path.exists():
            file_path.touch()
            print(f"Created {init_file}")


def get_available_providers():
    """Get list of available LLM providers"""
    providers = []
    
    # Try importing to check if libraries are available
    try:
        import openai
        if get_api_key("openai"):
            providers.append("openai")
    except ImportError:
        pass
    
    try:
        import anthropic
        if get_api_key("anthropic"):
            providers.append("anthropic")
    except ImportError:
        pass
        
    try:
        import google.generativeai as genai
        if get_api_key("google"):
            providers.append("google")
    except ImportError:
        pass
        
    try:
        import ollama
        # Ollama doesn't need an API key, just the library
        providers.append("ollama")
    except ImportError:
        pass
    
    return providers