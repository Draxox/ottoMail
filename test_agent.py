"""Test the complete agent workflow with a sample email"""
import asyncio
import json
from agent.graph import EmailAgentGraph
from agent.state import EmailAgentState
from integrations.llm_wrapper import UnifiedLLM, EnhancedMockService


async def test_agent():
    """Test agent with the example email from user"""
    
    # Example email from user's complaint
    test_email = {
        "id": "test_001",
        "from": "debabrata@financecorp.com",
        "subject": "AI Agent for Portfolio Management System - Development Inquiry",
        "body": """
        Hi,
        
        I'm Debabrata from a financial services company. We're looking for help building an AI agent 
        that can manage investment portfolios in real-time. The system needs to:
        
        - Track portfolio performance in real-time
        - Provide risk analysis and alerts
        - Suggest portfolio rebalancing strategies
        - Integrate with major stock exchanges
        - Include a professional dashboard
        
        We need something sophisticated that can handle complex financial calculations. 
        Are you able to help with this? What would be the timeline and cost?
        
        Looking forward to hearing from you.
        
        Best regards,
        Debabrata G.
        Finance Innovation Director
        """
    }
    
    print("=" * 80)
    print("TESTING OTTOMAIL AGENT WORKFLOW")
    print("=" * 80)
    print(f"\nTest Email:")
    print(f"From: {test_email['from']}")
    print(f"Subject: {test_email['subject']}")
    print(f"Body preview: {test_email['body'][:100]}...\n")
    
    # Create LLM and graph
    llm = UnifiedLLM()
    graph = EmailAgentGraph(llm)
    
    initial_state = {
        "messages": [],
        "email_id": test_email["id"],
        "email_from": test_email["from"],
        "email_subject": test_email["subject"],
        "email_body": test_email["body"],
        "thread_id": "test_001",
        "client_name": None,
        "company": None,
        "project_type": None,
        "requirements": None,
        "timeline": None,
        "budget": None,
        "project_plan": None,
        "cost_estimate": None,
        "proposal_text": None,
        "is_valid_inquiry": False,
        "confidence_score": 0.0,
        "needs_human_review": False,
        "current_step": "starting",
        "error": None
    }
    
    print("Executing agent workflow...\n")
    result = await graph.graph.ainvoke(initial_state)
    
    # Display results
    print("=" * 80)
    print("CLASSIFICATION RESULTS")
    print("=" * 80)
    print(f"Valid Inquiry: {result.get('is_valid_inquiry')}")
    confidence = result.get('confidence_score', 0)
    if isinstance(confidence, (int, float)):
        print(f"Confidence: {confidence:.0%}" if confidence <= 1 else f"Confidence: {confidence}%")
    else:
        print(f"Confidence: {confidence}")
    print(f"Reason: {result.get('error', 'N/A')}\n")
    
    print("=" * 80)
    print("EXTRACTED INFORMATION")
    print("=" * 80)
    print(f"Client Name: {result.get('client_name', 'N/A')}")
    print(f"Company: {result.get('company', 'N/A')}")
    print(f"Project Type: {result.get('project_type', 'N/A')}")
    print(f"Timeline: {result.get('timeline', 'N/A')}")
    print(f"Budget: {result.get('budget', 'N/A')}")
    print(f"\nRequirements:")
    requirements = result.get('requirements')
    if requirements and isinstance(requirements, list):
        for i, req in enumerate(requirements, 1):
            print(f"  {i}. {req}")
    else:
        print(f"  {requirements}")
    
    print("\n" + "=" * 80)
    print("PROJECT PLAN")
    print("=" * 80)
    plan = result.get('project_plan', {})
    if plan:
        print(f"Complexity: {plan.get('complexity', 'N/A')}")
        print(f"Total Hours: {plan.get('total_estimated_hours', 'N/A')}")
        print(f"\nPhases:")
        for phase in plan.get('phases', []):
            print(f"\n  • {phase.get('name', 'N/A')}")
            print(f"    Duration: {phase.get('duration', 'N/A')}")
            print(f"    Hours: {phase.get('hours', 'N/A')}")
            if 'tasks' in phase:
                print(f"    Tasks:")
                for task in phase.get('tasks', []):
                    print(f"      - {task}")
    else:
        print("No project plan generated")
    
    print("\n" + "=" * 80)
    print("COST ESTIMATE")
    print("=" * 80)
    cost = result.get('cost_estimate', {})
    if cost:
        min_val = cost.get('min', 'N/A')
        max_val = cost.get('max', 'N/A')
        print(f"Min: ${min_val:,}" if isinstance(min_val, int) else f"Min: {min_val}")
        print(f"Max: ${max_val:,}" if isinstance(max_val, int) else f"Max: {max_val}")
        sugg = cost.get('suggested', 'N/A')
        print(f"Suggested: ${sugg:,}\n" if isinstance(sugg, int) else f"Suggested: {sugg}\n")
    else:
        print("No cost estimate generated\n")
    
    print("=" * 80)
    print("GENERATED PROPOSAL")
    print("=" * 80)
    proposal = result.get('proposal_text', 'N/A')
    if proposal and proposal != 'N/A':
        print(proposal)
    else:
        print("No proposal text generated")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Final Status: {result.get('current_step', 'unknown')}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(test_agent())
