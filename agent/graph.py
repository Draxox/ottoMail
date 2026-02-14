from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agent.state import EmailAgentState
from agent.nodes import EmailAgentNodes
from langchain_openai import ChatOpenAI

class EmailAgentGraph:
    """
    LangGraph workflow with conditional routing
    Pro: Visual, debuggable, production-ready
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.nodes = EmailAgentNodes(self.llm)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        # Initialize graph with state
        workflow = StateGraph(EmailAgentState)
        
        # Add nodes
        workflow.add_node("classify", self.nodes.classify_email)
        workflow.add_node("extract", self.nodes.extract_requirements)
        workflow.add_node("plan", self.nodes.generate_project_plan)
        workflow.add_node("cost", self.nodes.calculate_cost)
        workflow.add_node("propose", self.nodes.generate_proposal)
        workflow.add_node("store", self.nodes.store_in_database)
        workflow.add_node("draft", self.nodes.create_email_draft)
        workflow.add_node("notify", self.nodes.send_notification)
        
        # Define conditional routing (Pro Tip from web:43)
        def should_process(state: EmailAgentState) -> str:
            """Router: Only process valid inquiries"""
            if state["is_valid_inquiry"]:
                return "extract"
            return END
        
        def should_notify(state: EmailAgentState) -> str:
            """Router: Notify if needs human review"""
            if state["needs_human_review"]:
                return "notify"
            return END
        
        # Build workflow
        workflow.set_entry_point("classify")
        
        workflow.add_conditional_edges(
            "classify",
            should_process,
            {
                "extract": "extract",
                END: END
            }
        )
        
        # Linear flow for valid emails
        workflow.add_edge("extract", "plan")
        workflow.add_edge("plan", "cost")
        workflow.add_edge("cost", "propose")
        workflow.add_edge("propose", "store")
        workflow.add_edge("store", "draft")
        
        workflow.add_conditional_edges(
            "draft",
            should_notify,
            {
                "notify": "notify",
                END: END
            }
        )
        
        workflow.add_edge("notify", END)
        
        # Add memory for checkpointing (crash recovery)
        memory = MemorySaver()
        
        return workflow.compile(checkpointer=memory)
    
    async def process_email(self, email_data: dict) -> dict:
        """
        Execute the full workflow
        Returns final state
        """
        
        initial_state = {
            "messages": [],
            "email_id": email_data["id"],
            "email_from": email_data["from"],
            "email_subject": email_data["subject"],
            "email_body": email_data["body"],
            "is_valid_inquiry": False,
            "needs_human_review": False,
            "processing_step": "started",
            "confidence_score": 0.0
        }
        
        # Execute graph with tracing (Pro Tip from web:45)
        config = {"configurable": {"thread_id": email_data["id"]}}
        
        final_state = await self.graph.ainvoke(initial_state, config)
        
        return final_state
