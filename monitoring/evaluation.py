from langsmith import evaluate
from typing import List, Dict

class ProposalEvaluator:
    """
    Automated quality evaluation
    Pro Tip from web:45: Multi-level evaluation
    """
    
    @staticmethod
    async def evaluate_proposal_quality(proposal_text: str) -> Dict[str, float]:
        """
        Evaluate proposal on multiple dimensions
        """
        
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(model="gpt-4o")
        
        eval_prompt = f"""Evaluate this proposal on these criteria (0-10 scale):

1. Professionalism: Tone and language quality
2. Clarity: Clear explanation of approach
3. Completeness: Includes all necessary elements
4. Persuasiveness: Likely to win the client

Proposal:
{proposal_text}

Return JSON: {{"professionalism": X, "clarity": X, "completeness": X, "persuasiveness": X, "overall": X}}
"""
        
        response = await llm.ainvoke(eval_prompt)
        scores = json.loads(response.content)
        
        return scores
    
    @staticmethod
    async def batch_evaluate_recent_proposals(limit: int = 10):
        """
        Evaluate recent proposals to track quality trends
        Run this daily via Celery task
        """
        
        from integrations.storage import StorageService
        
        storage = StorageService()
        proposals = await storage.get_recent_proposals(limit)
        
        results = []
        for proposal in proposals:
            scores = await ProposalEvaluator.evaluate_proposal_quality(
                proposal["proposal_text"]
            )
            results.append({
                "proposal_id": proposal["id"],
                "scores": scores
            })
        
        # Store evaluation results for trend analysis
        avg_quality = sum(r["scores"]["overall"] for r in results) / len(results)
        
        print(f"Average Proposal Quality: {avg_quality}/10")
        
        return results
