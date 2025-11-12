"""
Researcher Mode Utilities
Advanced features for academic research and paper analysis
"""

class ResearchAssistant:
    """Provides research-focused capabilities"""
    
    def __init__(self, llm_caller, agent_prompt):
        """
        Initialize the research assistant
        
        Args:
            llm_caller: Function to call LLM with messages
            agent_prompt: System prompt from learning mentor agent
        """
        self.call_llm = llm_caller
        self.agent_prompt = agent_prompt
    
    def generate_literature_review(self, topic, notes_content):
        """Generate a structured literature review outline"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the research notes below about "{topic}", create a structured literature review outline including:
1. Key themes and patterns in the literature
2. Major findings and consensus
3. Gaps or contradictions in current research
4. Suggested areas for further investigation

Notes:
{notes_content}"""}
            ],
            temperature=0.6
        )
        
        return response if response else None
    
    def suggest_research_questions(self, notes_content):
        """Generate potential research questions based on notes"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following research notes, suggest 5-7 potential research questions that would:
- Address gaps in current knowledge
- Build on existing findings
- Explore practical applications
- Challenge assumptions

Format as a numbered list with brief justification for each.

Notes:
{notes_content}"""}
            ],
            temperature=0.7
        )
        
        return response if response else None
    
    def generate_methodology_suggestions(self, research_topic, notes_content):
        """Suggest appropriate research methodologies"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the research topic "{research_topic}" and notes below, suggest appropriate research methodologies:
- Quantitative approaches
- Qualitative approaches
- Mixed methods
- Data collection techniques
- Analysis methods

Explain why each would be suitable.

Notes:
{notes_content}"""}
            ],
            temperature=0.6
        )
        
        return response if response else None
    
    def identify_key_papers(self, notes_content):
        """Identify seminal papers and key citations to explore"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the research notes below, identify and suggest:
- Seminal papers that should be cited (with likely authors if recognizable from content)
- Key researchers in this field
- Important journals or conferences
- Classic papers vs. recent advances

Notes:
{notes_content}"""}
            ],
            temperature=0.5
        )
        
        return response if response else None
    
    def generate_hypothesis(self, notes_content):
        """Generate testable hypotheses based on research notes"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the following research notes, generate 3-5 testable hypotheses that:
- Are specific and measurable
- Build on existing knowledge
- Have clear independent and dependent variables
- Could lead to meaningful findings

Format as:
**H1:** [Hypothesis statement]
- Rationale: [Why this matters]
- How to test: [Suggested approach]

Notes:
{notes_content}"""}
            ],
            temperature=0.7
        )
        
        return response if response else None
    
    def create_theoretical_framework(self, notes_content):
        """Develop a theoretical framework from research notes"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Based on the research notes below, develop a theoretical framework that:
- Identifies key constructs and concepts
- Shows relationships between variables
- Grounds the work in existing theory
- Provides a conceptual foundation

Include a suggested visual representation in Mermaid diagram format.

Notes:
{notes_content}"""}
            ],
            temperature=0.6
        )
        
        return response if response else None
    
    def generate_citation_analysis(self, notes_content):
        """Analyze citation patterns and suggest citation strategies"""
        if not notes_content.strip():
            return None
        
        response = self.call_llm(
            messages=[
                {"role": "system", "content": self.agent_prompt},
                {"role": "user", "content": f"""Analyze the research notes and provide:
- Suggested citation strategy (how to cite key ideas)
- Important theoretical foundations to cite
- Recent empirical work to reference
- Methodological papers to cite

Format with specific guidance on building a strong citation network.

Notes:
{notes_content}"""}
            ],
            temperature=0.6
        )
        
        return response if response else None
