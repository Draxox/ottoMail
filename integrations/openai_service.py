"""Multi-LLM service with fallback"""
import os
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic_settings import BaseSettings

class LLMConfig(BaseSettings):
    LLM_PROVIDER: Literal["openai", "gemini"] = "openai"
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

config = LLMConfig()

class LLMService:
    def __init__(self):
        self.llm = self._create_llm()
    
    def _create_llm(self):
        """Create LLM with automatic fallback"""
        try:
            if config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
                return ChatOpenAI(
                    model=config.LLM_MODEL,
                    api_key=config.OPENAI_API_KEY,
                    temperature=0.3
                )
        except:
            pass
        
        # Fallback to Gemini (free tier)
        try:
            if config.GOOGLE_API_KEY:
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=config.GOOGLE_API_KEY,
                    temperature=0.3
                )
        except:
            pass
        
        raise Exception("No working LLM configured. Set OPENAI_API_KEY or GOOGLE_API_KEY")
    
    async def invoke(self, prompt: str) -> str:
        """Invoke LLM and return response"""
        response = await self.llm.ainvoke(prompt)
        return response.content
