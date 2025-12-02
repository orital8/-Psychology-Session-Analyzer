import json
from openai import OpenAI
from config import settings

class SuperAdvisor:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_advice(self, user_query, user_history):
        # 1. Summarize History for Context
        # We flatten the history to extract just emotions and topics
        emotions_summary = []
        for session in user_history:
            if isinstance(session, list):
                for utterance in session:
                    if "emotion" in utterance:
                        emotions_summary.append(utterance["emotion"])
        
        # Limit history to last 50 emotions to strictly avoid token limits
        recent_emotions = ", ".join(emotions_summary[-50:])

        system_prompt = f"""
        You are the 'Super Advisor', an advanced psychological AI.
        
        **User History (Recent Emotions):** {recent_emotions}
        
        **Task:** Based on the user's current thought and their emotional history, categorize their current state into one of these 4 categories:
        [Happy, Sad, Worried, Excited]
        
        Then, provide exactly 5 actionable, psychologically grounded advices.
        
        **Output JSON:**
        {{
            "detected_category": "...",
            "advices": ["1...", "2...", "3...", "4...", "5..."]
        }}
        """

        response = self.client.responses.create(
            model=settings.LLM_MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            text={ "format": { "type": "text" }, "verbosity": "medium" },
            reasoning={ "effort": "medium" }
        )

        try:
            if hasattr(response, 'output_text'):
                result = response.output_text
            elif hasattr(response, 'choices'):
                result = response.choices[0].message.content
            else:
                result = str(response)
        except:
            result = "{}"

        cleaned = result.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)