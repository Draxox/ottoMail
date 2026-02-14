"""Database storage service"""
from sqlalchemy.orm import Session
from app.models import SessionLocal, Client, Proposal
import json

class StorageService:
    def __init__(self):
        self.db = SessionLocal()
    
    def create_client(self, state):
        client = Client(
            name=state['client_name'],
            email=state['email_from'],
            company=state.get('company'),
            project_type=state['project_type'],
            requirements=json.dumps(state.get('requirements', [])),
            timeline=state.get('timeline'),
            budget=state.get('budget'),
            thread_id=state['thread_id']
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client.id
    
    def create_proposal(self, client_id, state, draft_id):
        proposal = Proposal(
            client_id=client_id,
            proposal_text=state['proposal_text'],
            cost_min=state['cost_estimate']['min'],
            cost_max=state['cost_estimate']['max'],
            draft_id=draft_id,
            status='pending'
        )
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal.id
    
    def get_pending_proposals(self):
        proposals = self.db.query(Proposal).filter(Proposal.status == 'pending').all()
        result = []
        for p in proposals:
            client = self.db.query(Client).filter(Client.id == p.client_id).first()
            result.append({
                'id': p.id,
                'client_name': client.name,
                'client_email': client.email,
                'project_type': client.project_type,
                'proposal_text': p.proposal_text,
                'cost_min': p.cost_min,
                'cost_max': p.cost_max,
                'status': p.status
            })
        return result
    
    def get_proposal(self, proposal_id):
        return self.db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    def approve_proposal(self, proposal_id):
        proposal = self.get_proposal(proposal_id)
        if proposal:
            proposal.approved = True
            proposal.status = 'approved'
            self.db.commit()
    
    def mark_sent(self, proposal_id):
        proposal = self.get_proposal(proposal_id)
        if proposal:
            proposal.status = 'sent'
            proposal.sent_at = datetime.utcnow()
            self.db.commit()
    
    def reject_proposal(self, proposal_id):
        proposal = self.get_proposal(proposal_id)
        if proposal:
            proposal.status = 'rejected'
            self.db.commit()
    
    def is_email_processed(self, email_id):
        # Simple check - expand later
        return False
    
    def close(self):
        self.db.close()
