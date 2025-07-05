from flask import current_app
from AI.groq_client import GroqClient
from AI.prompts import PromptLibrary


class AIService:
    """Main AI service that coordinates all AI features"""

    def __init__(self):
        self.enabled = current_app.config.get('AI_ENABLED', 'false').lower() == 'true'
        if self.enabled:
            try:
                self.groq_client = GroqClient()
                self.prompts = PromptLibrary()
            except Exception as e:
                print(f"Warning: AI service initialization failed: {e}")
                self.enabled = False

    def is_enabled(self) -> bool:
        """Check if AI features are enabled"""
        return self.enabled

    def analyze_task_priority(self, title: str, description: str = "", occupation : str = "") -> str:
        """
        Analyze task priority using AI
        Returns: 'Low', 'Medium', 'High', or 'Critical'
        """
        if not self.enabled:
            return 'Medium'  # Default when AI is disabled

        try:
            prompt = self.prompts.get_priority_prompt(title, description, occupation)
            response = self.groq_client.chat_completion(prompt, max_tokens=10, temperature=0.1)

            # Simple validation - check if response contains valid priority
            response = response.strip().title()
            valid_priorities = ['Low', 'Medium', 'High', 'Critical']

            for priority in valid_priorities:
                if priority.lower() in response.lower():
                    return priority

            return 'Medium'  # Fallback if no valid priority found

        except Exception as e:
            print(f"Error in priority analysis: {e}")
            return 'Medium'  # Safe fallback