from supabase import create_client, Client
from typing import Dict, Optional, List
from uuid import UUID
import os

class StorageService:
    """
    MCP-compliant storage interface
    Abstracts database operations
    """
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)
    
    async def create_client(
        self,
        name: str,
        email: str,
        project_type: str,
        requirements: List[str],
        original_email: str
    ) -> UUID:
        """Store new client"""
        
        data = {
            "client_name": name,
            "client_email": email,
            "project_type": project_type,
            "requirements": requirements,
            "original_email_body": original_email,
            "status": "new"
        }
        
        result = self.client.table("clients").insert(data).execute()
        return result.data[0]["id"]
    
    async def create_proposal(
        self,
        client_id: UUID,
        plan: Dict,
        text: str,
        cost_min: int,
        cost_max: int
    ) -> UUID:
        """Store proposal"""
        
        data = {
            "client_id": str(client_id),
            "project_plan": plan,
            "proposal_text": text,
            "estimated_cost_min": cost_min,
            "estimated_cost_max": cost_max,
            "status": "pending_approval"
        }
        
        result = self.client.table("proposals").insert(data).execute()
        return result.data[0]["id"]
    
    async def get_pending_proposals(self) -> List[Dict]:
        """Fetch proposals needing approval"""
        
        result = self.client.table("proposals") \
            .select("*") \
            .eq("status", "pending_approval") \
            .execute()
        
        return result.data
    
    async def approve_proposal(self, proposal_id: UUID) -> bool:
        """Mark proposal as approved"""
        
        self.client.table("proposals") \
            .update({"status": "approved", "approved_by_human": True}) \
            .eq("id", str(proposal_id)) \
            .execute()
        
        return True
