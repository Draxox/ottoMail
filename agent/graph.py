"""LangGraph workflow orchestration"""
from langgraph.graph import StateGraph, END
from .state import EmailAgentState
from .nodes import AgentNodes
from integrations.openai_service import LLMService

class EmailAgentGraph:
    def __init__(self, llm: LLMService):
        self.nodes = AgentNodes(llm)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(EmailAgentState)
        
        # Add all nodes
        workflow.add_node("classify", self.nodes.classify_email)
        workflow.add_node("extract", self.nodes.extract_requirements)
        workflow.add_node("plan", self.nodes.generate_plan)
        workflow.add_node("cost", self.nodes.calculate_cost)
        workflow.add_node("propose", self.nodes.generate_proposal)
        
        # Entry point
        workflow.set_entry_point("classify")
        
        # Conditional routing
        def route_after_classify(state):
            return "extract" if state["is_valid_inquiry"] else END
        
        workflow.add_conditional_edges(
            "classify",
            route_after_classify,
            {"extract": "extract", END: END}
        )
        
        # Linear flow for valid emails
        workflow.add_edge("extract", "plan")
        workflow.add_edge("plan", "cost")
        workflow.add_edge("cost", "propose")
        workflow.add_edge("propose", END)
        
        return workflow.compile()
    
    async def process_email(self, email_data: dict) -> dict:
        """Process single email through complete workflow"""
        initial_state = {
            "messages": [],
            "email_id": email_data["id"],
            "email_from": email_data["from"],
            "email_subject": email_data["subject"],
            "email_body": email_data["body"],
            "thread_id": email_data["thread_id"],
            "is_valid_inquiry": False,
            "confidence_score": 0.0,
            "needs_human_review": True,
            "current_step": "started",
            "error": None
        }
        
        return await self.graph.ainvoke(initial_state)
