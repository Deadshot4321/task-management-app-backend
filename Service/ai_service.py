from flask import current_app
from AI.groq_client import GroqClient
from AI.prompts import PromptLibrary


class AIService:
    """Main AI service that coordinates all AI features"""

    def __init__(self):
        ai_enabled = current_app.config.get('AI_ENABLED', False)
        # Handle both boolean and string values
        if isinstance(ai_enabled, bool):
            self.enabled = ai_enabled
        else:
            self.enabled = str(ai_enabled).lower() == 'true'
        
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

    def analyze_task_tags(self, title: str, description: str = "") -> list:
        """
        Analyze task content and generate relevant tags using AI
        Returns: List of tag names (up to 3)
        """
        if not self.enabled:
            return ['Work']  # Default when AI is disabled

        try:
            import json
            prompt = self.prompts.get_tag_prompt(title, description)
            response = self.groq_client.chat_completion(prompt, max_tokens=50, temperature=0.3)

            # Parse JSON response
            response = response.strip()
            
            # Try to extract JSON array from response
            if '[' in response and ']' in response:
                # Extract the JSON array part
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end]
                
                tags = json.loads(json_str)
                
                # Validate tags are strings and from allowed list
                valid_tags = []
                allowed_tags = [
                    'Work', 'Personal', 'Health', 'Finance', 'Learning', 
                    'Urgent', 'Shopping', 'Travel', 'Meeting', 'Project'
                ]
                
                for tag in tags:
                    if isinstance(tag, str) and tag in allowed_tags:
                        valid_tags.append(tag)
                    elif isinstance(tag, str):
                        # Try to find close match
                        tag_lower = tag.lower()
                        for allowed_tag in allowed_tags:
                            if tag_lower == allowed_tag.lower():
                                valid_tags.append(allowed_tag)
                                break
                
                # Limit to 3 tags
                return valid_tags[:3] if valid_tags else ['Work']
            
            # Fallback parsing for non-JSON responses
            response_lower = response.lower()
            fallback_tags = []
            allowed_tags = [
                'Work', 'Personal', 'Health', 'Finance', 'Learning', 
                'Urgent', 'Shopping', 'Travel', 'Meeting', 'Project'
            ]
            
            for tag in allowed_tags:
                if tag.lower() in response_lower:
                    fallback_tags.append(tag)
                if len(fallback_tags) >= 3:
                    break
            
            return fallback_tags if fallback_tags else ['Work']

        except Exception as e:
            print(f"Error in tag analysis: {e}")
            return ['Work']  # Safe fallback