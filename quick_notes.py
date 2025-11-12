#!/usr/bin/env python3
"""
Quick Notes System with Learning Mentor Integration

This script allows users to take notes quickly when the main note-taking system
is not running, and integrates with the learning mentor agent for guidance.
"""

import os
import datetime
import re
import json
from pathlib import Path

# Try to import API libraries, but don't require them
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    genai = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

import sys
from pathlib import Path

# Add project root to path for config import
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import OPENAI_MODEL, ANTHROPIC_MODEL, OLLAMA_MODEL, GOOGLE_MODEL, DEFAULT_LLM_PROVIDER

class QuickNoteTakingSystem:
    def __init__(self):
        self.project_dir = Path.home() / "Projects" / "notes"
        self.topics_dir = self.project_dir / "topics"
        self.daily_notes_dir = self.project_dir / "daily_notes"
        self.current_session_notes = []
        self.session_date = datetime.date.today().strftime("%Y-%m-%d")
        
        # Set up API if available
        self.setup_api()

        # Ask user for topic or create general topic
        self.topic = self.identify_topic_from_user()
        self.notes_file = self.topics_dir / self.topic / f"{self.session_date}.md"
        self.daily_notes_file = self.daily_notes_dir / f"{self.session_date}_{self.topic}.md"

        # Ensure directories exist
        (self.topics_dir / self.topic).mkdir(parents=True, exist_ok=True)
        self.daily_notes_dir.mkdir(parents=True, exist_ok=True)

        print(f"Starting quick note-taking session for {self.session_date}")
        print(f"Notes will be saved to: {self.notes_file}")
        print(f"Daily notes will be saved to: {self.daily_notes_file}")

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

    def call_llm(self, messages, max_tokens=500, temperature=0.7, provider=None):
        """
        Generic method to call any available LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
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
                response = openai.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            elif provider == "anthropic" and self.use_anthropic:
                # Use Anthropic
                system_message = ""
                user_messages = []
                
                # Separate system message from user/assistant messages
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        user_messages.append(msg)
                
                response = self.client_anthropic.messages.create(
                    model=ANTHROPIC_MODEL,
                    system=system_message,
                    messages=user_messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.content[0].text
            elif provider == "ollama" and self.use_ollama:
                # Use Ollama
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
                # Combine messages into a single prompt for Gemini
                prompt = ""
                for msg in messages:
                    role = msg["role"]
                    content = msg["content"]
                    prompt += f"{role}: {content}\n"
                
                model = genai.GenerativeModel(GOOGLE_MODEL)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature
                    )
                )
                return response.text
            else:
                # Fallback to local logic if no provider is available
                return None
        except Exception as e:
            print(f"Error calling {provider} API: {e}")
            return None

    def identify_topic_from_user(self):
        """Prompt user to specify a topic for the session"""
        print("\nWhat topic would you like to focus on today?")
        print("Examples: 'machine-learning', 'web-development', 'programming', 'data-science'")
        topic = input("Enter topic (or press Enter for 'general'): ").strip()

        if not topic:
            topic = 'general'

        # Sanitize topic name (convert to lowercase, replace spaces with hyphens)
        topic = re.sub(r'[^\w\s-]', '', topic).strip().lower().replace(' ', '-')
        return topic

    def capture_notes(self, user_input):
        """Capture user input as-is in both topic and daily files"""
        # Write to the topic-specific file
        with open(self.notes_file, "a", encoding="utf-8") as f:
            f.write(f"{user_input}\n")
        
        # Write to the daily notes file
        with open(self.daily_notes_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {self.topic}: {user_input}\n")
            
        self.current_session_notes.append(user_input)
        print(f"✓ Notes captured: {user_input[:50]}...")

    def get_learning_guidance(self, note_content):
        """Get learning guidance from the LLM based on the notes"""
        if not self.primary_llm:
            return "No LLM provider is configured. Please check your API keys in the .env file."
        
        # Create a system message for learning guidance
        system_message = """You are an educational learning mentor. Based on the user's notes, provide:
        1. Clarification on any unclear concepts
        2. Suggestions for deeper understanding
        3. Questions to think about
        4. Connections to other topics
        5. Recommendations for further study
        
        Keep your response focused and helpful."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Provide learning guidance based on these notes: {note_content}"}
        ]
        
        response = self.call_llm(messages=messages, max_tokens=600, temperature=0.7)
        
        if response:
            return response
        else:
            return "I'm having trouble providing learning guidance. Please make sure your API keys are properly configured."

    def consolidate_daily_notes(self):
        """Create a consolidated daily summary with learning insights"""
        if self.daily_notes_file.exists():
            with open(self.daily_notes_file, "r", encoding="utf-8") as f:
                daily_content = f.read()
            
            if daily_content.strip():
                # If API is available, generate additional content
                additional_content = self.generate_learning_summary_with_llm(daily_content)
                
                summary_filename = self.daily_notes_dir / f"summary_{self.session_date}_{self.topic}.md"
                
                summary_content = f"""# Daily Learning Summary - {self.session_date} ({self.topic})

## Notes Captured
{daily_content}

## Learning Insights and Summary
{additional_content}

## Key Takeaways
- Review these concepts regularly
- Identify areas that need more focus
- Plan next steps for continued learning

"""
                with open(summary_filename, "w", encoding="utf-8") as f:
                    f.write(summary_content)
                
                print(f"✓ Daily summary created: {summary_filename}")
                return summary_filename
        return None

    def generate_learning_summary_with_llm(self, original_notes):
        """Generate a learning summary using LLM"""
        if self.primary_llm and original_notes.strip():
            # Use primary LLM for generating learning summary
            summary_messages = [
                {"role": "system", "content": """You are an educational assistant. Based on the notes provided,
                create a concise learning summary that includes:
                1. Key concepts covered
                2. Main points or takeaways
                3. Areas for further study
                4. Questions to consider
                5. Practical applications or next steps
                
                Format your response in markdown with clear sections."""},
                {"role": "user", "content": original_notes}
            ]
            
            summary_response = self.call_llm(
                messages=summary_messages,
                max_tokens=600,
                temperature=0.6
            )
            
            if summary_response:
                return summary_response
            else:
                return "Could not generate learning summary. Please check your API configuration."
        else:
            return "No learning summary generated - LLM not available."

def main():
    qnts = QuickNoteTakingSystem()

    print("\nQuick Note-Taking System with Learning Mentor")
    print("Type 'done for the day' when you've finished your session")
    print("Type 'guidance' to get learning mentor advice on your notes")
    print("Type 'quit' to exit without consolidating")
    print("-" * 50)

    while True:
        user_input = input("\nEnter your notes or command: ").strip()

        if user_input.lower() == "done for the day":
            print("\nConsolidating your daily notes with learning insights...")
            qnts.consolidate_daily_notes()
            print("Thank you for your learning session! Notes and summary have been saved.")
            break
        elif user_input.lower() == "guidance":
            if qnts.current_session_notes:
                last_note = qnts.current_session_notes[-1]
                print(f"\nGetting learning guidance for: {last_note[:100]}...")
                guidance = qnts.get_learning_guidance(last_note)
                print(f"\nLearning Guidance:\n{guidance}")
            else:
                print("No notes captured yet. Please add some notes first.")
        elif user_input.lower() == "quit":
            print("Exiting without consolidation.")
            break
        elif user_input:
            qnts.capture_notes(user_input)
        else:
            print("Please enter some notes or a command.")

if __name__ == "__main__":
    main()