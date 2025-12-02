import json
import hashlib
import redis
import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger("analyzer_service")

class LLMAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            decode_responses=True
        )

    def analyze_transcript(self, transcript_data):
        # 1. Create a unique Cache Key
        transcript_text = json.dumps(transcript_data)
        cache_key = f"analysis:{hashlib.md5(transcript_text.encode()).hexdigest()}"
        
        # 2. Check Cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Cache Hit! Returning saved analysis from Redis.")
            return json.loads(cached_result)

        logger.info("Cache Miss. Calling OpenAI (GPT-5 Nano)...")
        
        # 3. System Prompt (Deep Psychological Focus)
        system_prompt = """
        You are an expert clinical psychologist specializing in Psychodynamic and Emotionally Focused Therapy (EFT).
        Your task is to analyze the following therapy session transcript to uncover the subtext and latent emotions.

        **Analysis Goals:**
        1. **Role Identification**: Identify 'Therapist' vs 'Patient' based on inquiry patterns vs disclosure patterns.
        2. **Deep Psychoanalysis**: For EACH utterance, identify:
           - **Explicit Topic**: What is said.
           - **Latent Emotion**: The felt sense or underlying feeling (e.g., "Anxious Vulnerability" instead of just "Sad").
           - **Subtext**: The unspoken meaning, defense mechanisms, or attachment needs.
        3. **Clinical Recommendations**: Provide actionable interventions for the therapist.

        **Constraints:**
        - Output MUST be valid, parseable JSON.
        - Do NOT create images.
        - Do NOT use markdown code blocks (```json). Just the raw JSON object.
        
        **Output JSON Structure:**
        {
            "participants": {"Speaker A": "Role", "Speaker B": "Role"},
            "analysis": [
                {"speaker": "A", "text": "...", "topic": "...", "emotion": "...", "subtext": "..."}
            ],
            "clinical_recommendations": "..."
        }
        """

        # 4. Call OpenAI (Using new Responses API syntax)
        # We inject our prompts into the 'input' list
        response = self.client.responses.create(
            model="gpt-5-nano",
            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Analyze this transcript: {transcript_text}"
                }
            ],
            text={
                "format": {
                    "type": "text" 
                },
                "verbosity": "medium"
            },
            reasoning={
                "effort": "medium"
            },
            tools=[],
            store=True,
            include=[
                "reasoning.encrypted_content",
                "web_search_call.action.sources"
            ]
        )

        # 5. Extract Output
       
        try:
            # Try new format attribute if available, else standard
            if hasattr(response, 'output_text'):
                result = response.output_text
            elif hasattr(response, 'choices'):
                result = response.choices[0].message.content
            else:
                # Fallback for specific response types
                result = str(response) 
        except Exception:
            # If structure is totally new, dump it to string to debug, but assume text property
            result = response.text if hasattr(response, 'text') else ""

        # Clean up result (remove markdown if model added it despite instructions)
        cleaned_result = result.replace("```json", "").replace("```", "").strip()

        # 6. Save to Cache
        self.cache.setex(cache_key, 86400, cleaned_result)
        
        return json.loads(cleaned_result)