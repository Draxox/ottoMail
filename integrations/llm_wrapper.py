from pydantic_settings import BaseSettings
from typing import Literal, Optional
from integrations.local_llm import LocalLLMService
from integrations.gemini_service import GeminiService

class LLMConfig(BaseSettings):
    LLM_PROVIDER: Literal["local", "gemini", "mock"] = "mock"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

config = LLMConfig()

class UnifiedLLM:
    _instance = None

    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.service = self._create_service()

    def _create_service(self):
        p = str(self.provider).strip().lower()
        print(f"Initializing LLM Provider: {p.upper()}")
        
        if p == "gemini":
            try:
                return GeminiService()
            except Exception as e:
                print(f"Failed to init Gemini: {e}")
                return EnhancedMockService()
        
        if p == "local":
            try:
                return LocalLLMService()
            except Exception as e:
                print(f"Failed to init Local LLM: {e}")
                return EnhancedMockService()
            
        return EnhancedMockService()

    async def invoke(self, prompt: str) -> str:
        return await self.service.invoke(prompt)


class EnhancedMockService:
    """Context-aware mock service for testing and development"""
    
    async def invoke(self, prompt: str) -> str:
        """Generate context-aware mock responses based on prompt type"""
        print(f"[MOCK LLM]: {prompt[:60]}...")
        
        if "Classify if this email" in prompt or "Analyze this email" in prompt:
            if "finance" in prompt.lower() or "portfolio" in prompt.lower():
                return '{"is_valid": true, "confidence": 0.95, "reason": "Valid financial services inquiry"}'
            return '{"is_valid": true, "confidence": 0.9, "reason": "Valid business inquiry"}'
        
        elif "Extract structured information" in prompt or "Extract structured client information" in prompt:
            if "portfolio" in prompt.lower() or "finance" in prompt.lower():
                return '{"client_name": "Debabrata G.","company": "Finance Company","email": "debabrata@financecorp.com","project_type": "AI Agent for Portfolio Management System","requirements": ["Real-time portfolio tracking","Risk analysis and alerts","Automated trading suggestions","Historical performance analytics","Integration with multiple brokers"],"timeline": "3 months","budget": "$15000-$20000"}'
            return '{"client_name": "John Doe","company": "Tech Startup","email": "john@startup.com","project_type": "Web Application","requirements": ["React frontend","Python backend","Database","User auth","API"],"timeline": "2 months","budget": "$10000-$15000"}'
        
        elif "Create a realistic project plan" in prompt or "Create project breakdown" in prompt:
            if "complex" in prompt.lower() or "portfolio" in prompt.lower():
                return '{"complexity": "complex","total_estimated_hours": 160,"phases": [{"name": "Phase 1: Discovery & Requirements","duration": "1.5 weeks","hours": 20,"tasks": ["Detailed requirements gathering","Technical design","Architecture review","Security planning"]},{"name": "Phase 2: Core Backend Development","duration": "3 weeks","hours": 60,"tasks": ["Database design","API endpoints","Authentication","Integration services"]},{"name": "Phase 3: Frontend & User Interface","duration": "2 weeks","hours": 40,"tasks": ["UI/UX design","React components","State management","Responsive design"]},{"name": "Phase 4: Testing & Quality Assurance","duration": "1.5 weeks","hours": 25,"tasks": ["Unit tests","Integration tests","Performance testing","Security audit"]},{"name": "Phase 5: Deployment & Handoff","duration": "1 week","hours": 15,"tasks": ["Production setup","Documentation","Staff training","Support plan"]}]}'
            return '{"complexity": "medium","total_estimated_hours": 80,"phases": [{"name": "Phase 1: Planning & Design","duration": "1 week","hours": 15,"tasks": ["Requirements analysis","UI mockups","Database schema"]},{"name": "Phase 2: Development","duration": "2 weeks","hours": 40,"tasks": ["Backend development","Frontend development","Integration"]},{"name": "Phase 3: Testing & Launch","duration": "1 week","hours": 25,"tasks": ["Testing","Fixes","Deployment"]}]}'
        
        elif "Write a professional" in prompt or "Write professional proposal" in prompt or "Write proposal" in prompt:
            if "portfolio" in prompt.lower() or "finance" in prompt.lower():
                return """Dear Debabrata,

Thank you for reaching out. We're excited about your AI Agent for Portfolio Management System project.

**Understanding Your Vision**
Your project requires an intelligent system that can analyze portfolios in real-time, provide risk assessments, suggest trading opportunities, and integrate with multiple brokerage platforms.

**Our Approach**
We follow a phased development methodology with regular feedback and testing to ensure quality.

**Project Breakdown**
- Phase 1: Discovery & Design (1.5 weeks, $2,400)
- Phase 2: Core Backend (3 weeks, $4,800)
- Phase 3: Frontend & Dashboards (2 weeks, $3,200)
- Phase 4: Testing & Optimization (1.5 weeks, $2,400)
- Phase 5: Launch & Documentation (1 week, $1,600)

**Total Investment: $14,400 - $17,600**

**Next Steps**
Let's schedule a call to discuss your requirements and provide a detailed proposal.

Best regards,
OttoMail Solutions"""
            
            return """Dear Client,

Thank you for your inquiry. We're interested in discussing your web application project.

**Project Overview**
We understand you need a custom web application and we have extensive experience building similar solutions.

**Our Process**
1. Requirements gathering and analysis
2. Design and planning
3. Development and implementation
4. Testing and quality assurance
5. Deployment and support

**Investment Range**
$10,000 - $15,000

**Timeline**
Typically 2-3 months

**Next Steps**
Let's schedule a call to discuss your specific needs.

Best regards,
OttoMail Solutions"""
        
        return '{"response": "Mock service response"}'
