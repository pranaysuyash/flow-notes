"""
Learning Enhancement Utilities
Provides AI-powered features to enhance note-taking and learning
"""

class LearningEnhancer:
    """Generates learning aids using LLM"""
    
    def __init__(self, llm_caller, agent_prompt):
        """
        Initialize the learning enhancer
        
        Args:
            llm_caller: Function to call LLM with messages
            agent_prompt: System prompt from learning mentor agent
        """
        self.call_llm = llm_caller
        self.agent_prompt = agent_prompt
    
    def generate_auto_tags(self, notes_content):
        """Extract key concepts and tags from notes"""
        if not notes_content.strip():
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
        if not notes_content.strip():
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
        if not notes_content.strip():
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
        if not notes_content.strip():
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
        if not notes_content.strip():
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
        if not notes_content.strip():
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
        if not notes_content.strip():
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
