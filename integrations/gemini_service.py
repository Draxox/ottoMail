from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic_settings import BaseSettings

class GeminiConfig(BaseSettings):
    GOOGLE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

config = GeminiConfig()

class GeminiService:
    def __init__(self):
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required for Gemini Service")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.3
        )

    async def invoke(self, prompt: str) -> str:
        """Invoke Gemini LLM and return response text"""
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            print(f"[Gemini Error] Fallback triggered: {e}")
            # For extraction prompts, raise the exception so nodes.py can handle intelligent fallback
            if "Extract structured information" in prompt:
                raise  # Let nodes.py handle the intelligent name parsing fallback
            # Check prompt type to return valid JSON for other cases
            elif "Classify if this email" in prompt:
                return '{"is_valid": true, "confidence": 0.5, "reason": "Fallback: Gemini API Error"}'
            elif "Create a realistic project plan" in prompt:
                return '{"complexity": "low","total_estimated_hours": 10,"phases": [{"name": "Phase 1","duration": "1 week","hours": 10,"tasks": ["Initial Consultation"]}]}'
            elif "Write a professional" in prompt:
                return f"Dear Client,\\n\\nThank you for your email. We are currently experiencing high demand on our AI servers. Please contact us directly to discuss your project.\\n\\nBest regards,\\nOttoMail (Fallback Mode)"
            return '{"response": "Error in Gemini API"}'
