from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from agent.state import EmailAgentState
import json

class EmailAgentNodes:
    """
    Individual processing nodes in the agent workflow
    Each node is a pure function: State -> State
    """
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    async def classify_email(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 1: Classify if email is a valid business inquiry
        Uses AI to filter spam, auto-replies, etc.
        """
        
        prompt = f"""Analyze this email and determine if it's a genuine business inquiry.

Email Subject: {state['email_subject']}
Email Body: {state['email_body']}

Respond with JSON:
{{
    "is_valid_inquiry": true/false,
    "confidence": 0.0-1.0,
    "reason": "explanation",
    "inquiry_type": "website_redesign" | "mobile_app" | "consulting" | "other"
}}
"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content="You are an email classifier for a software agency."),
            HumanMessage(content=prompt)
        ])
        
        result = json.loads(response.content)
        
        return {
            **state,
            "is_valid_inquiry": result["is_valid_inquiry"],
            "confidence_score": result["confidence"],
            "processing_step": "classified"
        }
    
    async def extract_requirements(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 2: Extract structured client data using OpenAI Structured Outputs
        Pro Tip: Use JSON Schema for guaranteed structure
        """
        
        from pydantic import BaseModel, Field
        from typing import List
        
        class ClientRequirements(BaseModel):
            client_name: str = Field(description="Person's name from signature or body")
            company: Optional[str] = Field(description="Company name if mentioned")
            project_type: str = Field(description="Type of project requested")
            requirements: List[str] = Field(description="List of specific requirements")
            timeline: Optional[str] = Field(description="Desired timeline")
            budget: str = Field(description="Budget information or 'Flexible'")
        
        # Structured output ensures reliability (Pro Tip from web:45)
        structured_llm = self.llm.with_structured_output(ClientRequirements)
        
        prompt = f"""Extract structured client information from this email:

Subject: {state['email_subject']}
Body: {state['email_body']}
From: {state['email_from']}

Extract all requirements mentioned explicitly or implicitly."""
        
        extracted = await structured_llm.ainvoke(prompt)
        
        return {
            **state,
            "extracted_data": extracted.dict(),
            "processing_step": "extracted"
        }
    
    async def generate_project_plan(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 3: Create task breakdown using AI with ReAct pattern
        """
        
        extracted = state["extracted_data"]
        
        prompt = f"""As a senior project manager, create a detailed project breakdown.

Project Type: {extracted['project_type']}
Requirements: {', '.join(extracted['requirements'])}
Timeline: {extracted.get('timeline', 'To be determined')}

Generate a JSON project plan with:
- phases (array of {{name, tasks, duration}})
- total_estimated_hours (integer)
- complexity_level (simple/medium/complex)
"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content="You are a project planning expert. Return only valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        project_plan = json.loads(response.content)
        
        return {
            **state,
            "project_plan": project_plan,
            "processing_step": "planned"
        }
    
    async def calculate_cost(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 4: Business logic for cost calculation
        No AI needed - pure business rules
        """
        
        plan = state["project_plan"]
        hours = plan.get("total_estimated_hours", 40)
        complexity = plan.get("complexity_level", "medium")
        
        # Your business logic
        base_rate = 50
        multipliers = {"simple": 1.0, "medium": 1.5, "complex": 2.0}
        
        base_cost = hours * base_rate * multipliers.get(complexity, 1.5)
        
        cost_estimate = {
            "min": int(base_cost * 0.9),
            "max": int(base_cost * 1.1),
            "hours": hours,
            "complexity": complexity
        }
        
        return {
            **state,
            "cost_estimate": cost_estimate,
            "processing_step": "costed"
        }
    
    async def generate_proposal(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 5: Generate professional proposal text
        """
        
        extracted = state["extracted_data"]
        plan = state["project_plan"]
        cost = state["cost_estimate"]
        
        phases_text = "\n".join([
            f"- {phase['name']}: {phase['duration']}" 
            for phase in plan['phases']
        ])
        
        prompt = f"""Write a professional proposal email for:

Client: {extracted['client_name']}
Company: {extracted.get('company', 'their organization')}
Project: {extracted['project_type']}

Key Points:
{phases_text}

Timeline: {extracted.get('timeline', '6-8 weeks')}
Cost: ${cost['min']:,} - ${cost['max']:,}

Tone: Professional but friendly, concise (200-250 words)
Include: Understanding of needs, our approach, timeline, cost, next steps
"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content="You are a professional business proposal writer."),
            HumanMessage(content=prompt)
        ])
        
        return {
            **state,
            "proposal_text": response.content,
            "processing_step": "proposal_generated"
        }
    
    async def store_in_database(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 6: Persist to database
        """
        
        from integrations.storage import StorageService
        
        storage = StorageService()
        
        # Store client
        client_id = await storage.create_client(
            name=state["extracted_data"]["client_name"],
            email=state["email_from"],
            project_type=state["extracted_data"]["project_type"],
            requirements=state["extracted_data"]["requirements"],
            original_email=state["email_body"]
        )
        
        # Store proposal
        proposal_id = await storage.create_proposal(
            client_id=client_id,
            plan=state["project_plan"],
            text=state["proposal_text"],
            cost_min=state["cost_estimate"]["min"],
            cost_max=state["cost_estimate"]["max"]
        )
        
        return {
            **state,
            "client_id": str(client_id),
            "proposal_id": str(proposal_id),
            "processing_step": "stored"
        }
    
    async def create_email_draft(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 7: Create Gmail draft (never auto-send)
        Pro Tip #1: Human review before sending
        """
        
        from integrations.gmail_mcp import GmailMCP
        
        gmail = GmailMCP()
        
        subject = f"{state['extracted_data']['project_type']} Proposal"
        if state['extracted_data'].get('company'):
            subject += f" – {state['extracted_data']['company']}"
        
        draft_id = await gmail.create_draft(
            to=state["email_from"],
            subject=subject,
            body=state["proposal_text"]
        )
        
        return {
            **state,
            "processing_step": "draft_created",
            "needs_human_review": True
        }
    
    async def send_notification(self, state: EmailAgentState) -> EmailAgentState:
        """
        Node 8: Notify human for approval
        Pro Tip #3: Human-in-the-loop
        """
        
        from integrations.telegram_service import TelegramService
        
        telegram = TelegramService()
        
        message = f"""
🔔 New Proposal Ready

👤 {state['extracted_data']['client_name']}
📋 {state['extracted_data']['project_type']}
💰 ${state['cost_estimate']['min']:,} - ${state['cost_estimate']['max']:,}

Review at: /proposals/{state['proposal_id']}
"""
        
        await telegram.send_message(message)
        
        return {
            **state,
            "processing_step": "notified"
        }
