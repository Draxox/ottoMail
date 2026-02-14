"""Shared state management for LangGraph"""
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class EmailAgentState(TypedDict):
    """Complete agent state"""
    # Input
    messages: Annotated[List[BaseMessage], add_messages]
    email_id: str
    email_from: str
    email_subject: str
    email_body: str
    thread_id: str
    
    # Extracted data
    client_name: Optional[str]
    company: Optional[str]
    project_type: Optional[str]
    requirements: Optional[List[str]]
    timeline: Optional[str]
    budget: Optional[str]
    
    # Generated content
    project_plan: Optional[dict]
    cost_estimate: Optional[dict]
    proposal_text: Optional[str]
    
    # Control flags
    is_valid_inquiry: bool
    confidence_score: float
    needs_human_review: bool
    current_step: str
    error: Optional[str]
