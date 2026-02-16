"""Individual agent processing nodes"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from integrations.llm_wrapper import UnifiedLLM

class AgentNodes:
    def __init__(self, llm: UnifiedLLM):
        self.llm = llm
    
    def _clean_json(self, response: str) -> str:
        """Clean markdown formatting from JSON response"""
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return response.strip()

    async def classify_email(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 1: Classify if business inquiry with clear rules"""
        prompt = f"""Classify if this email is a genuine business inquiry needing a proposal.

RULES - Email IS VALID if:
- Person asks about building/developing something (app, website, tool, system, etc.)
- Person asks for consulting, training, or professional services
- Person describes a business problem needing a solution
- Message is reasonably detailed (not one-word spam)

Rules - Email IS NOT VALID if:
- It\'s spam, promotional, or recruiting
- It\'s a job application
- It\'s generic "I\'ll pay you big money" with no details
- It\'s obviously auto-generated marketing

Email to analyze:
Subject: {state['email_subject']}
From: {state['email_from']}
Body: {state['email_body']}

Return ONLY valid JSON:
{{
    "is_valid": true or false,
    "confidence": 0.0 to 1.0,
    "reason": "one sentence explanation"
}}"""
        
        response = None
        try:
            response = await self.llm.invoke(prompt)
            result = json.loads(self._clean_json(response))
            
            print(f"[DEBUG] Classification Result: {result}")
            state.update({
                "is_valid_inquiry": result["is_valid"],
                "confidence_score": result["confidence"],
                "classification_reason": result.get("reason", "No reason provided"),
                "current_step": "classified"
            })
        except Exception as e:
            # Check if response was empty or blocked
            if not response and not str(e):
                error_msg = "Empty response from LLM"
            else:
                error_msg = f"LLM Error: {str(e)}"
                
            state.update({
                "is_valid_inquiry": False,
                "confidence_score": 0.0,
                "current_step": "classification_failed",
                "error": error_msg
            })
        
        return state
    
    async def extract_requirements(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 2: Extract client data with detailed guidance"""
        prompt = f"""Extract structured information from this inquiry email.

Email:
From: {state['email_from']}
Subject: {state['email_subject']}
Body: {state['email_body']}

EXTRACTION GUIDELINES:
- client_name: Look for signature, name mentions, or parse from email address
- company: Business name if mentioned, otherwise null or infer from domain
- project_type: What they want built (be SPECIFIC, e.g., "Custom CRM for Real Estate", not just "CRM")
- requirements: 3-5 specific features or requirements mentioned
- timeline: When they need it (e.g., "ASAP", "3 months", "Q1 2026")
- budget: Any budget mentioned, or "Flexible" if not stated

EXAMPLE OUTPUT:
{{
    "client_name": "Debabrata G.",
    "company": "Investment Firm",
    "email": "debabrata@example.com",
    "project_type": "AI Portfolio Management System",
    "requirements": ["Real-time tracking", "Risk analysis", "Trading alerts"],
    "timeline": "3 months",
    "budget": "$15000-$25000"
}}

Return ONLY valid JSON with extracted data:"""
        
        try:
            response = await self.llm.invoke(prompt)
            data = json.loads(self._clean_json(response))
            
            state.update({
                **data,
                "current_step": "extracted"
            })
        except Exception as e:
            # Intelligent fallback: parse name from email address
            email_from = state['email_from']
            # Extract name from email (e.g., "krishguptano12@gmail.com" -> "Krish Gupta")
            if '<' in email_from:
                # Format: "Name <email@example.com>"
                client_name = email_from.split('<')[0].strip()
            else:
                # Format: "email@example.com" - parse username
                username = email_from.split('@')[0]
                # Remove numbers and split camelCase/snake_case
                import re
                name_parts = re.sub(r'[0-9_.-]', ' ', username).strip()
                client_name = ' '.join(word.capitalize() for word in name_parts.split())
            
            state.update({
                "client_name": client_name or "Valued Client",
                "company": None,
                "project_type": state.get('email_subject', 'Custom Project'),
                "requirements": ["Discuss detailed requirements"],
                "timeline": "To be determined",
                "budget": "Flexible",
                "current_step": "extraction_fallback",
                "error": str(e)
            })
        
        return state
    
    async def generate_plan(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 3: Create detailed 5-phase project breakdown"""
        requirements = ', '.join(state.get('requirements', []))
        
        prompt = f"""Create a realistic project plan for this inquiry.

Project: {state['project_type']}
Client: {state['client_name']}
Company: {state.get('company', 'Unknown')}
Requirements: {requirements}
Timeline: {state.get('timeline', 'Not specified')}

PLANNING GUIDELINES:
- Generate 5 phases: Discovery, Core Dev, Frontend/UI, Testing, Deployment
- Assign realistic duration and hours per phase
- Each phase has 4-5 specific tasks
- Complexity levels: simple (40-80 hrs), medium (80-120 hrs), complex (120-200 hrs)
- For finance/portfolio projects: assume COMPLEX (160 hrs)
- For generic/simple projects: assume MEDIUM (80 hrs)

EXAMPLE COMPLEX PROJECT (160 hours):
{{
    "complexity": "complex",
    "total_estimated_hours": 160,
    "phases": [
        {{
            "name": "Phase 1: Discovery & Requirements",
            "duration": "1.5 weeks",
            "hours": 20,
            "tasks": ["Detailed requirements gathering", "Technical design", "Architecture review", "Security planning"]
        }},
        {{
            "name": "Phase 2: Core Backend Development",
            "duration": "3 weeks",
            "hours": 60,
            "tasks": ["Database design", "API endpoints", "Authentication", "Integration services"]
        }},
        {{
            "name": "Phase 3: Frontend & User Interface",
            "duration": "2 weeks",
            "hours": 40,
            "tasks": ["UI/UX design", "React components", "State management", "Responsive design"]
        }},
        {{
            "name": "Phase 4: Testing & Quality Assurance",
            "duration": "1.5 weeks",
            "hours": 25,
            "tasks": ["Unit tests", "Integration tests", "Performance testing", "Security audit"]
        }},
        {{
            "name": "Phase 5: Deployment & Handoff",
            "duration": "1 week",
            "hours": 15,
            "tasks": ["Production setup", "Documentation", "Staff training", "Support plan"]
        }}
    ]
}}

Return ONLY valid JSON with project plan:"""
        
        try:
            response = await self.llm.invoke(prompt)
            state["project_plan"] = json.loads(self._clean_json(response))
            state["current_step"] = "planned"
        except Exception as e:
            # Fallback based on project type
            is_complex = "portfolio" in state['project_type'].lower() or "finance" in state['project_type'].lower()
            
            if is_complex:
                hours = 160
                complexity = "complex"
            else:
                hours = 80
                complexity = "medium"
            
            state["project_plan"] = {
                "complexity": complexity,
                "total_estimated_hours": hours,
                "phases": [
                    {"name": "Phase 1: Discovery", "tasks": ["Requirements", "Design", "Planning"], "duration": "1-2 weeks", "hours": hours // 5},
                    {"name": "Phase 2: Development", "tasks": ["Backend", "Frontend", "Integration"], "duration": "2-3 weeks", "hours": hours // 5 * 2},
                    {"name": "Phase 3: Testing", "tasks": ["QA", "Bug fixes", "Optimization"], "duration": "1 week", "hours": hours // 5},
                    {"name": "Phase 4: Deployment", "tasks": ["Staging", "Launch", "Monitoring"], "duration": "1 week", "hours": hours // 5},
                ]
            }
            state["current_step"] = "planned_fallback"
        
        return state
    
    async def calculate_cost(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 4: Pure business logic (no LLM)"""
        from app.services.cost_service import calculate_cost
        
        cost_data = calculate_cost(
            state["project_plan"]["total_estimated_hours"],
            state["project_plan"]["complexity"]
        )
        
        state["cost_estimate"] = cost_data
        state["current_step"] = "costed"
        return state
    
    async def generate_proposal(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node 5: Generate detailed professional proposal email"""
        phases = state["project_plan"]["phases"]
        phases_text = "\n".join([f"• {p['name']}: {p['duration']} ({p.get('hours', '?')} hours)" for p in phases])
        cost = state["cost_estimate"]
        
        prompt = f"""Write a professional, personalized proposal email body (NO email headers, NO subject line).

CLIENT DETAILS:
Name: {state['client_name']}
Email: {state['email_from']}
Company: {state.get('company', 'their organization')}
Project: {state['project_type']}

PROJECT PLAN:
{phases_text}

BUSINESS TERMS:
Total Hours: {state['project_plan']['total_estimated_hours']}
Complexity: {state['project_plan']['complexity']}
Investment: ${cost['min']:,} - ${cost['max']:,}
Timeline: {state.get('timeline', '8-12 weeks')}

CRITICAL REQUIREMENTS:
- Address the client by their ACTUAL name: {state['client_name']}
- Sign with "OttoMail Solutions Team" (NO placeholders like [Your Name])
- Use proper paragraph breaks (double newlines between sections)
- DO NOT use placeholders like [Company Name] or [Your Name] - use actual values
- Be specific about the project type: {state['project_type']}

PROPOSAL STRUCTURE:
1. Greeting: Address {state['client_name']} personally
2. Understanding: Show you understand their {state['project_type']} needs
3. Approach: Your methodology and why it works
4. Project Breakdown: Summarize the 5 phases with clear formatting
5. Investment: Cost range ${cost['min']:,} - ${cost['max']:,} and what's included
6. Business Value: Why this is worth the investment
7. Next Steps: Clear call-to-action (schedule call, etc.)
8. Sign-off: "Best regards,\nOttoMail Solutions Team"

TONE: Professional, confident, business-focused (not salesy)
LENGTH: 400-600 words
FORMATTING: Use double line breaks between sections for readability

Return ONLY the email body text (no JSON, no markdown formatting, just plain text with line breaks):"""
        
        try:
            state["proposal_text"] = await self.llm.invoke(prompt)
            state["current_step"] = "proposal_generated"
        except Exception as e:
            state["proposal_text"] = f"""Dear {state['client_name']},

Thank you for reaching out regarding your {state['project_type']} project. We're excited about this opportunity.

**Understanding Your Needs**
Based on your inquiry, we understand you need a sophisticated solution with specific requirements including {state['requirements'][0] if state['requirements'] else 'custom functionality'}. We have experience delivering projects of this complexity and scope.

**Our Approach**
We follow a structured 5-phase development methodology:

{phases_text}

This phased approach ensures quality at each stage and allows for regular feedback and adjustments.

**Project Investment**
Based on our analysis, the estimated investment for your project is:
- Total Development Hours: {state['project_plan']['total_estimated_hours']} hours
- Complexity Level: {state['project_plan']['complexity'].upper()}
- Cost Range: ${cost['min']:,} - ${cost['max']:,}
- Timeline: {state.get('timeline', '8-12 weeks')}

**Why This Investment**
This budget covers comprehensive development, rigorous testing, and deployment support. We focus on delivering long-term value and ensuring your system is maintainable and scalable.

**Next Steps**
We'd like to schedule a 30-minute discovery call to:
1. Confirm specific requirements
2. Discuss timeline and priorities
3. Address any questions
4. Provide a detailed project plan

Please let me know your availability for this week or next.

Best regards,
OttoMail Solutions"""
            state["current_step"] = "proposal_fallback"
        
        return state

