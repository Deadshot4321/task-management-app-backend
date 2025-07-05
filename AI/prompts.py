class PromptLibrary:
    """Centralized prompt templates for all AI features"""

    # Task Priority Analysis
    PRIORITY_PROMPT = """
You are a smart task prioritization assistant. Analyze this task considering the person's occupation and professional context.

Task: {title}
Description: {description}
User's Occupation: {occupation}

PRIORITY RULES:
- Critical: Immediate deadlines, production issues, emergency meetings, or tasks that block others
- High: Important work deadlines, key meetings, career-impacting tasks, or urgent professional responsibilities
- Medium: Regular work tasks, routine meetings, personal important tasks, or tasks with flexible timelines
- Low: Non-urgent personal tasks, optional activities, or tasks with distant deadlines

CONTEXT CONSIDERATIONS:
- If task relates to the user's occupation, increase priority appropriately
- Work-related tasks generally have higher priority during work hours
- Professional meetings and deadlines should be weighted higher
- Consider if delaying this task would impact the user's work or others

Respond with EXACTLY ONE WORD: Critical, High, Medium, or Low

Priority:"""

    # Task Tag Generation
    TAG_PROMPT = """
Based on the following task, generate up to 3 relevant one-word tags from this list:
[Work, Personal, Health, Finance, Learning, Urgent, Shopping, Travel, Meeting, Project]

Return them as a JSON array of strings. Choose only from the provided list. Be selective and choose the most relevant tags.

Task: {title}
Description: {description}

Example response: ["Work", "Meeting", "Urgent"]

Tags:"""


    @staticmethod
    def get_priority_prompt(title: str, description: str = "",occupation: str = "") -> str:
        return PromptLibrary.PRIORITY_PROMPT.format(
            title=title,
            description=description or "No description provided",
            occupation=occupation
        )
    
    @staticmethod
    def get_tag_prompt(title: str, description: str = "") -> str:
        return PromptLibrary.TAG_PROMPT.format(
            title=title,
            description=description or "No description provided"
        )
