from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class EmailAgentState(TypedDict):
    """
    Shared state across all agent nodes
    Pro: Type-safe state management prevents errors
    """
    # Input
    messages: Annotated[List[BaseMessage], add_messages]
    email_id: str
    email_from: str
    email_subject: str
    email_body: str
    
    # Processing stages
    extracted_data: Optional[dict]  # Client requirements extraction
    project_plan: Optional[dict]    # Task breakdown
    cost_estimate: Optional[dict]   # Pricing calculation
    proposal_text: Optional[str]    # Generated proposal
    
    # Database IDs
    client_id: Optional[str]
    proposal_id: Optional[str]
    
    # Decision flags
    is_valid_inquiry: bool
    needs_human_review: bool
    approval_status: Optional[str]
    
    # Metadata
    processing_step: str
    error_message: Optional[str]
    confidence_score: float  # AI extraction confidence
