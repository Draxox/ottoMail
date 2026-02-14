from langsmith import Client
from langsmith.run_helpers import traceable
import os

# Initialize LangSmith for tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "email-ai-copilot"

langsmith_client = Client()

@traceable(name="email_processing_workflow")
async def trace_email_processing(email_id: str, state: dict):
    """
    Wrap agent execution with tracing
    Pro Tip: See every step, measure latency, debug failures
    """
    
    # LangSmith automatically traces:
    # - Every LLM call
    # - Every tool execution
    # - State transitions
    # - Latencies
    # - Token usage
    
    return state

# Custom metrics tracking
class MetricsCollector:
    """Track business metrics"""
    
    @staticmethod
    async def log_email_processed(
        email_id: str,
        processing_time: float,
        confidence: float,
        cost_estimate: int
    ):
        """Log to your analytics system"""
        
        metrics = {
            "event": "email_processed",
            "email_id": email_id,
            "processing_time_seconds": processing_time,
            "ai_confidence": confidence,
            "estimated_value": cost_estimate,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to monitoring (Datadog, Grafana, etc.)
        # Or store in database for analytics
        print(f"METRIC: {metrics}")
