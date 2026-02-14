"""Individual agent processing nodes"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from integrations.openai_service import LLMService

class AgentNodes:
    def __init__(self, llm: LLMService):
        self.llm = llm
    
    async def classify_email(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 1: Classify if business inquiry"""
        prompt = f"""
        Analyze this email and determine if it's a genuine business inquiry.
        
        Subject: {state['email_subject']}
        From: {state['email_from']}
        Body: {state['email_body']}
        
        Return JSON only:
        {{
            "is_valid": true/false,
            "confidence": 0.0-1.0,
            "reason": "brief explanation"
        }}
        """
        
        try:
            response = await self.llm.invoke(prompt)
            result = json.loads(response)
            
            state.update({
                "is_valid_inquiry": result["is_valid"],
                "confidence_score": result["confidence"],
                "current_step": "classified"
            })
        except Exception as e:
            state.update({
                "is_valid_inquiry": False,
                "confidence_score": 0.0,
                "current_step": "classification_failed",
                "error": str(e)
            })
        
        return state
    
    async def extract_requirements(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 2: Extract client data"""
        prompt = f"""
        Extract structured client information. Return JSON only.
        
        From: {state['email_from']}
        Subject: {state['email_subject']}
        Body: {state['email_body']}
        
        {{
            "client_name": "name from signature/body",
            "company": "company name or null",
            "project_type": "main project type",
            "requirements": ["req1", "req2", ...],
            "timeline": "timeline or null",
            "budget": "budget info or 'Flexible'"
        }}
        """
        
        try:
            response = await self.llm.invoke(prompt)
            data = json.loads(response)
            
            state.update({
                **data,
                "current_step": "extracted"
            })
        except:
            state.update({
                "client_name": "Unknown Client",
                "project_type": "General Inquiry",
                "requirements": ["Manual review needed"],
                "current_step": "extraction_failed"
            })
        
        return state
    
    async def generate_plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 3: Create project plan"""
        requirements = ', '.join(state.get('requirements', []))
        
        prompt = f"""
        Create project breakdown for: {state['project_type']}
        Requirements: {requirements}
        
        Return JSON only:
        {{
            "phases": [
                {{"name": "Phase 1", "tasks": ["task1", "task2"], "duration": "1 week"}},
                ...
            ],
            "total_hours": 40,
            "complexity": "simple|medium|complex"
        }}
        """
        
        try:
            response = await self.llm.invoke(prompt)
            state["project_plan"] = json.loads(response)
            state["current_step"] = "planned"
        except:
            state["project_plan"] = {
                "phases": [{"name": "Standard Project", "tasks": ["Planning", "Development", "Review"], "duration": "4-6 weeks"}],
                "total_hours": 40,
                "complexity": "medium"
            }
            state["current_step"] = "planned_fallback"
        
        return state
    
    async def calculate_cost(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 4: Pure business logic (no LLM)"""
        from app.services.cost_service import calculate_cost
        
        cost_data = calculate_cost(
            state["project_plan"]["total_hours"],
            state["project_plan"]["complexity"]
        )
        
        state["cost_estimate"] = cost_data
        state["current_step"] = "costed"
        return state
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 5: Generate proposal text"""
        phases = state["project_plan"]["phases"]
        phases_text = "\n".join([f"• {p['name']}: {p['duration']}" for p in phases])
        cost = state["cost_estimate"]
        
        prompt = f"""
        Write professional proposal email (BODY ONLY):
        
        Client: {state['client_name']}
        Company: {state.get('company', 'their organization')}
        Project: {state['project_type']}
        
        Scope:
        {phases_text}
        
        Cost: ${cost['min']:,} - ${cost['max']:,}
        Timeline: {state.get('timeline', '4-6 weeks')}
        
        Tone: Professional, friendly, concise (200 words).
        Include: Understanding needs, our approach, timeline, cost, next steps.
        """
        
        try:
            state["proposal_text"] = await self.llm.invoke(prompt)
            state["current_step"] = "proposal_generated"
        except Exception as e:
            state["proposal_text"] = f"""
            Dear {state['client_name']},
            
            Thank you for your inquiry about {state['project_type']}. We're excited to help!
            
            Our proposed approach:
            {phases_text}
            
            Estimated timeline: {state.get('timeline', '4-6 weeks')}
            Investment: ${cost['min']:,} - ${cost['max']:,}
            
            Next steps:
            1. Schedule discovery call
            2. Finalize requirements
            3. Kickoff project
            
            Best regards,
            Your Development Team
            """
            state["current_step"] = "proposal_fallback"
        
        return state
