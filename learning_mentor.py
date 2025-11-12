#!/usr/bin/env python3
"""
Learning Mentor Agent with LLM Integration

This script provides a learning mentor functionality that can guide users
through learning topics even without the full note-taking system.
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

from config import OPENAI_MODEL, ANTHROPIC_MODEL, OLLAMA_MODEL, GOOGLE_MODEL, DEFAULT_LLM_PROVIDER

class LearningMentorAgent:
    def __init__(self):
        self.setup_api()
        self.conversation_history = []
        print("Learning Mentor Agent initialized!")
        print("I'm here to help guide you through your learning journey.")
        print("Type 'help' to see available commands, or just start learning!")
        print("-" * 50)

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

    def get_learning_response(self, user_input):
        """Get a learning-focused response from the LLM"""
        if not self.primary_llm:
            return "No LLM provider is configured. Please check your API keys in the .env file."
        
        # Create a system message for the learning mentor
        system_message = """You are an educational learning mentor. Your role is to:
        1. Explain concepts clearly and thoroughly
        2. Provide examples when helpful
        3. Suggest next steps for learning
        4. Answer questions in a helpful, encouraging manner
        5. Break down complex topics into manageable parts
        6. Suggest resources and practice exercises when appropriate
        
        Be supportive and encouraging while maintaining educational rigor."""
        
        # Create messages for the LLM
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history to maintain context
        messages.extend(self.conversation_history)
        
        # Add the user's current input
        messages.append({"role": "user", "content": user_input})
        
        # Get response from LLM
        response = self.call_llm(messages=messages, max_tokens=800, temperature=0.7)
        
        if response:
            # Add user input and response to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep only the last 10 interactions to avoid context overflow
            if len(self.conversation_history) > 20:  # 10 user-assistant pairs
                self.conversation_history = self.conversation_history[-20:]
                
            return response
        else:
            return "I'm having trouble connecting to the learning service. Please make sure your API keys are properly configured."

    def get_study_plan(self, topic):
        """Generate a study plan for a specific topic"""
        if not self.primary_llm:
            return "No LLM provider is configured. Please check your API keys in the .env file."
        
        system_message = """You are an educational learning mentor. Create a structured study plan that includes:
        1. Prerequisites (what should be known first)
        2. Learning objectives
        3. Study materials and resources
        4. Practice exercises
        5. Timeline suggestions
        6. Assessment methods
        
        Format your response in a clear, well-structured format."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Create a detailed study plan for learning {topic}"}
        ]
        
        response = self.call_llm(messages=messages, max_tokens=1000, temperature=0.6)
        
        if response:
            return response
        else:
            return f"Could not generate a study plan for {topic}. Please check your API configuration."

    def provide_learning_summary(self, current_topic):
        """Provide a summary of what was learned about a topic"""
        if not self.primary_llm:
            return "No LLM provider is configured. Please check your API keys in the .env file."
        
        system_message = """You are an educational learning mentor. Provide a comprehensive summary of the learning session,
        including key concepts, important points, and recommendations for further study."""
        
        # Create context from conversation history
        conversation_context = ""
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]
            conversation_context += f"{role}: {content}\n\n"
        
        if not conversation_context.strip():
            conversation_context = f"We just started discussing {current_topic}."
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Provide a learning summary based on our discussion about {current_topic}:\n\n{conversation_context}"}
        ]
        
        response = self.call_llm(messages=messages, max_tokens=600, temperature=0.5)
        
        if response:
            return response
        else:
            return "Could not generate a learning summary. Please check your API configuration."

    def show_help(self):
        """Display available commands"""
        help_text = """
Available commands:
- 'study_plan <topic>': Get a structured study plan for a topic
- 'summary': Get a summary of what we've learned
- 'quit' or 'exit': Exit the learning mentor
- 'clear': Clear the conversation history
- 'help': Show this help message

You can also just type your questions or topics you want to learn about!
        """
        return help_text

def main():
    mentor = LearningMentorAgent()
    current_topic = "general"
    
    while True:
        user_input = input("\nWhat would you like to learn about? ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nThank you for learning with me! Goodbye!")
            break
        elif user_input.lower() == 'help':
            print(mentor.show_help())
        elif user_input.lower() == 'clear':
            mentor.conversation_history = []
            print("Conversation history cleared.")
        elif user_input.lower().startswith('study_plan '):
            topic = user_input[11:].strip()  # Extract topic after 'study_plan '
            if topic:
                print(f"\nGenerating study plan for: {topic}")
                plan = mentor.get_study_plan(topic)
                print(f"\n{plan}")
                current_topic = topic
            else:
                print("Please specify a topic. Usage: study_plan <topic>")
        elif user_input.lower() == 'summary':
            summary = mentor.provide_learning_summary(current_topic)
            print(f"\n{summary}")
        elif user_input:
            response = mentor.get_learning_response(user_input)
            print(f"\n{response}")
        else:
            print("Please enter a question or topic to learn about.")

if __name__ == "__main__":
    main()