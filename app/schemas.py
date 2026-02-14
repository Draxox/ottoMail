"""Pydantic schemas"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClientSchema(BaseModel):
    id: int
    name: str
    email: str
    project_type: str
    status: str
    created_at: datetime

class ProposalSchema(BaseModel):
    id: int
    client_name: str
    client_email: str
    project_type: str
    proposal_text: str
    cost_min: int
    cost_max: int
    status: str
    created_at: datetime

class ApprovalRequest(BaseModel):
    approved: bool
