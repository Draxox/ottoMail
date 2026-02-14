"""API routes"""
from fastapi import APIRouter, HTTPException
from integrations.gmail_mcp import GmailMCP
from integrations.storage import StorageService
from agent.graph import EmailAgentGraph
from integrations.openai_service import LLMService
from app.schemas import ProposalSchema, ApprovalRequest

router = APIRouter()

@router.post("/check-emails")
async def check_emails():
    """Process unread emails"""
    gmail = GmailMCP()
    llm = LLMService()
    agent = EmailAgentGraph(llm)
    storage = StorageService()
    
    emails = await gmail.get_unread_emails()
    results = []
    
    for email in emails:
        # Skip processed emails
        if storage.is_email_processed(email["id"]):
            continue
            
        state = await agent.process_email(email)
        
        if not state["is_valid_inquiry"]:
            await gmail.mark_as_read(email["id"])
            continue
        
        # Save to database
        client_id = storage.create_client(state)
        draft_id = await gmail.create_draft(
            to=state["email_from"],
            subject=f"{state['project_type']} Proposal",
            body=state["proposal_text"],
            thread_id=state["thread_id"]
        )
        proposal_id = storage.create_proposal(client_id, state, draft_id)
        
        await gmail.mark_as_read(email["id"])
        results.append({"proposal_id": proposal_id, "status": "success"})
    
    return {"processed": len(results)}

@router.get("/proposals/pending")
async def get_pending_proposals():
    storage = StorageService()
    proposals = storage.get_pending_proposals()
    return proposals

@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: int, request: ApprovalRequest):
    storage = StorageService()
    gmail = GmailMCP()
    
    proposal = storage.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    
    if request.approved:
        storage.approve_proposal(proposal_id)
        await gmail.send_draft(proposal["draft_id"])
        storage.mark_sent(proposal_id)
        return {"message": "Proposal approved and sent!"}
    else:
        storage.reject_proposal(proposal_id)
        return {"message": "Proposal rejected"}
