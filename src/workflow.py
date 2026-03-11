from langgraph.graph import END, StateGraph
from .state import GraphState
from .nodes import Nodes

class Workflow():
    def __init__(self):
        # initialize graph state and nodes
        workflow = StateGraph(GraphState)
        nodes = Nodes()

        # register nodes
        workflow.add_node("load_new_emails", nodes.load_new_emails)
        workflow.add_node("is_email_box_empty", nodes.is_email_box_empty)
        workflow.add_node("is_email_spam", nodes.is_email_spam)
        workflow.add_node("categorize_email", nodes.categorize_email)
        workflow.add_node("get_grounded_response_from_rag", nodes.get_grounded_response_from_rag)
        workflow.add_node("email_writer", nodes.write_draft_email)
        workflow.add_node("email_proofreader", nodes.verify_generated_email)
        workflow.add_node("create_draft_response", nodes.create_draft_response)
        workflow.add_node("skip_unrelated_email", nodes.skip_unrelated_email)

        # entry point
        workflow.set_entry_point("load_new_emails")

        # check inbox
        workflow.add_edge("load_new_emails", "is_email_box_empty")
        workflow.add_conditional_edges(
            "is_email_box_empty",
            nodes.is_email_box_empty,
            {
                "process": "is_email_spam",
                "empty": END
            }
        )
        
        #check spam
        workflow.add_conditional_edges(
            "is_email_spam",
            nodes.is_email_spam,
            {
                "spam": "is_email_box_empty",
                "process": "categorize_email"
            }
        )

        # route email based on category
        workflow.add_conditional_edges(
            "categorize_email",
            nodes.route_email_based_on_category,
            {
                "product related": "get_grounded_response_from_rag",
                "downgrade": "email_writer",
                "not product related": "skip_unrelated_email"
            }
        )

        # RAG retrieval then email writing
        workflow.add_edge("get_grounded_response_from_rag", "email_writer")

        # generate and review email
        workflow.add_edge("email_writer", "email_proofreader")

        # proofreader decision
        workflow.add_conditional_edges(
            "email_proofreader",
            nodes.must_rewrite,
            {
                "send": "create_draft_response",
                "rewrite": "email_writer",
                "stop": "categorize_email"
            }
        )

        # continue checking inbox after processing
        workflow.add_edge("create_draft_response", "is_email_box_empty")
        workflow.add_edge("skip_unrelated_email", "is_email_box_empty")

        # compile workflow
        self.app = workflow.compile()