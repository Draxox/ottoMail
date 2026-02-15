"""Local LLM Service using GPT4All with GPU acceleration"""
import os
import sys
from pydantic_settings import BaseSettings

try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    GPT4All = None

class LLMConfig(BaseSettings):
    LLM_MODEL_PATH: str = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
    LLM_DEVICE: str = "gpu"  # Explicitly use GPU

    class Config:
        env_file = ".env"
        extra = "ignore"

config = LLMConfig()

class LocalLLMService:
    _model_instance = None

    def __init__(self):
        if not GPT4ALL_AVAILABLE:
            print("⚠️  gpt4all not installed. Install with: pip install gpt4all>=2.8.0")
            print("Falling back to Mock Service.")
            LocalLLMService._model_instance = None
            return
        
        if not LocalLLMService._model_instance:
            print(f"Loading Local LLM: {config.LLM_MODEL_PATH} on {config.LLM_DEVICE}...")
            try:
                # device='gpu' will auto-detect CUDA/Vulkan
                LocalLLMService._model_instance = GPT4All(
                    model_name=config.LLM_MODEL_PATH,
                    device=config.LLM_DEVICE,
                    allow_download=False,
                    n_ctx=8192
                )
                print(f"✅ Local LLM loaded successfully on {config.LLM_DEVICE.upper()}.")
                print("✅ GPU ACCELERATION: ACTIVE (Vulkan/CUDA)")
            except Exception as e:
                print(f"Failed to load Local LLM: {e}")
                print("Falling back to CPU...")
                try:
                    LocalLLMService._model_instance = GPT4All(
                        model_name=config.LLM_MODEL_PATH,
                        device="cpu",
                        allow_download=False # Don't block on download in main thread if it fails
                    )
                except Exception as e:
                    print(f"Could not load LLM (download likely in progress). Using Mock Fallback. Error: {e}")
                    LocalLLMService._model_instance = None

    async def invoke(self, prompt: str) -> str:
        """Invoke Local LLM and return response"""
        if not LocalLLMService._model_instance:
            return self._mock_fallback(prompt)
            
        import asyncio
        return await asyncio.to_thread(self._generate, prompt)

    def _mock_fallback(self, prompt: str) -> str:
        """Return mock responses when LLM is not ready"""
        print(f"Processing with Mock LLM (Model not loaded): {prompt[:50]}...")
        
        # Simple rule-based mock for our specific prompts
        if "Analyze this email" in prompt:
            return '{"is_valid": true, "confidence": 0.9, "reason": "Mock valid inquiry"}'
        elif "Extract structured client information" in prompt:
            return '{"client_name": "John Doe", "company": "Tech Corp", "project_type": "Web App", "requirements": ["React", "Python"], "timeline": "2 weeks", "budget": "$5000"}'
        elif "Create project breakdown" in prompt:
            return '{"phases": [{"name": "Phase 1", "tasks": ["Task A"], "duration": "1 week"}], "total_hours": 20, "complexity": "simple"}'
        elif "Write professional proposal" in prompt:
            return "Dear John,\n\nWe would love to build your Web App. It will cost $5000 and take 2 weeks.\n\nBest,\nOttoMail"
        
        return "Mock response"

    def _generate(self, prompt: str) -> str:
        output = LocalLLMService._model_instance.generate(
            prompt,
            max_tokens=1000,
            temp=0.7
        )
        return output
