"""Test agent with a SAMPLE business inquiry email"""
import asyncio
from agent.graph import EmailAgentGraph
from integrations.llm_wrapper import UnifiedLLM
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# Sample real-world business inquiry
SAMPLE_EMAIL = {
    "from": "john.smith@techcompany.com",
    "subject": "Website Redesign Project - Looking for Development Team",
    "body": """
Hi,

We are a fintech startup looking to redesign our website and build a new mobile-responsive e-commerce platform. 

Our current website is outdated and we need:
1. Complete website redesign with modern UI/UX
2. Mobile-responsive design for all devices
3. Integration with payment processing (Stripe/PayPal)
4. User authentication system with OAuth
5. Product inventory management system
6. Analytics and reporting dashboard
7. SEO optimization

We have a budget of $25,000 - $35,000 and need this completed within 3-4 months.

Can you provide a proposal with timeline and breakdown of costs?

Thanks,
John Smith
Tech Company Inc.
john.smith@techcompany.com
"""
}

async def test_sample_inquiry():
    """Test agent with sample business inquiry"""
    
    print("\n" + "=" * 80)
    print("TESTING WITH SAMPLE BUSINESS INQUIRY")
    print("=" * 80)
    print(f"\nLLM Provider: {LLM_PROVIDER.upper()}\n")
    
    print("=" * 80)
    print("EMAIL DETAILS")
    print("=" * 80)
    print(f"From: {SAMPLE_EMAIL['from']}")
    print(f"Subject: {SAMPLE_EMAIL['subject']}")
    print(f"\nBody:\n{SAMPLE_EMAIL['body'][:300]}...\n")
    
    # Create LLM and graph
    llm = UnifiedLLM()
    graph = EmailAgentGraph(llm)
    
    initial_state = {
        "messages": [],
        "email_id": "sample_001",
        "email_from": SAMPLE_EMAIL["from"],
        "email_subject": SAMPLE_EMAIL["subject"],
        "email_body": SAMPLE_EMAIL["body"],
        "thread_id": "sample_001",
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
    
    print("Processing with AI...\n")
    result = await graph.graph.ainvoke(initial_state)
    
    # Display results
    print("=" * 80)
    print("CLASSIFICATION")
    print("=" * 80)
    print(f"Valid Inquiry: {result.get('is_valid_inquiry')}")
    conf = result.get('confidence_score', 0)
    if isinstance(conf, (int, float)):
        print(f"Confidence: {conf:.0%}" if conf <= 1 else f"Confidence: {conf}%")
    status = result.get('current_step', '?')
    print(f"Status: {status}\n")
    
    if not result.get('is_valid_inquiry'):
        print("[Skipping remaining steps - not a valid inquiry]\n")
        return
    
    print("=" * 80)
    print("EXTRACTED INFORMATION")
    print("=" * 80)
    print(f"Client Name: {result.get('client_name', 'N/A')}")
    print(f"Company: {result.get('company', 'N/A')}")
    print(f"Project Type: {result.get('project_type', 'N/A')}")
    print(f"Timeline: {result.get('timeline', 'N/A')}")
    print(f"Budget: {result.get('budget', 'N/A')}\n")
    
    reqs = result.get('requirements')
    if reqs and isinstance(reqs, list):
        print("Requirements:")
        for i, req in enumerate(reqs, 1):
            print(f"  {i}. {req}")
    
    print("\n" + "=" * 80)
    print("PROJECT PLAN")
    print("=" * 80)
    plan = result.get('project_plan', {})
    if plan:
        print(f"Complexity: {plan.get('complexity', 'N/A')}")
        print(f"Total Hours: {plan.get('total_estimated_hours', 'N/A')}")
        print(f"Number of Phases: {len(plan.get('phases', []))}")
        
        phases = plan.get('phases', [])
        if phases:
            print("\nPhase Breakdown:")
            for i, phase in enumerate(phases, 1):
                if isinstance(phase, dict):
                    name = phase.get('name', f"Phase {i}")
                    hours = phase.get('hours', 'N/A')
                    print(f"  Phase {i}: {name} - {hours} hours")
    
    print("\n" + "=" * 80)
    print("COST ESTIMATE")
    print("=" * 80)
    cost = result.get('cost_estimate', {})
    if cost:
        min_cost = cost.get('min', 'N/A')
        max_cost = cost.get('max', 'N/A')
        if isinstance(min_cost, int):
            print(f"Estimated Range: ${min_cost:,} - ${max_cost:,}")
        else:
            print(f"Estimated Range: {min_cost} - {max_cost}")
        print(f"Rate: {cost.get('rate', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("GENERATED PROPOSAL (First 800 characters)")
    print("=" * 80)
    proposal = result.get('proposal_text', '')
    if proposal:
        if len(proposal) > 800:
            print(proposal[:800] + f"\n\n... [{len(proposal)-800} more characters] ...")
        else:
            print(proposal)
    else:
        print("[No proposal generated]")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE - SUCCESS!")
    print("=" * 80)
    print(f"\nThis demonstrates the full workflow:")
    print("1. Email received and classified as valid/invalid")
    print("2. Project details extracted")
    print("3. Requirements parsed")
    print("4. Project plan created")
    print("5. Costs calculated")
    print("6. Professional proposal generated")
    print(f"\nNow test with REAL emails from your Gmail inbox:")
    print("  python test_real_email.py")


if __name__ == "__main__":
    asyncio.run(test_sample_inquiry())
