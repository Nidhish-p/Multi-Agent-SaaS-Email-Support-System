from .agents import Agents
from .tools.gmail_manager import GmailManager
from .state import GraphState, Email
from .spam import SpamClassifier

class Nodes:
    def __init__(self):
        self.agents = Agents()
        self.gmail_tools = GmailManager()
        self.spam_classifier = SpamClassifier()

    def load_new_emails(self,graphstate) -> GraphState:
        print("Loading new emails...\n" )
        recent_emails = self.gmail_tools.fetch_unanswered_emails()
        emails = [Email(**email) for email in recent_emails]
        return {"emails": emails}

    def is_email_box_empty(self,graphstate) -> str:
        if len(graphstate['emails']) == 0:
            print("No new emails!!")
            return "empty"
        else:
            print("New emails to process.")
            return "process"
    
    def is_email_spam(self,graphstate):
        email = graphstate["emails"][-1]
        is_spam = self.spam_classifier.check(email)
        if is_spam:
            print("Email is spam!! \n")
            graphstate["emails"].pop()
            return "spam"
        else:
            return "process"

    def categorize_email(self,graphstate) -> GraphState:
        """Categorizes the current email using the categorize_email agent."""
        print("Checking email category...\n")
        
        current_email =graphstate["emails"][-1]
        result = self.agents.categorize_email.invoke({"email": current_email.body})
        print(f"Email category: {result.category}")
        
        return {
            "category": result.category,
            "tone": result.tone,
            "current_email": current_email
        }

    def route_email_based_on_category(self,graphstate) -> str:
        """Routes the email based on its category."""
        print("Routing email based on category...\n")
        category =graphstate["category"]
        if category in ["feature_query","pricing_upgrade","onboarding_help","technical_support"]:
            return "product related"
        elif category == "downgrade_cancellation":
            return "downgrade"
        elif category == "unrelated":
            return "not product related"

    def get_grounded_response_from_rag(self,graphstate) -> GraphState:
        """Retrieves information from internal knowledge based on RAG questions."""
        print("Retrieving information from internal knowledge...\n")
        current_email = graphstate["current_email"]
        grounded_response = self.agents.generate_rag_answer.invoke(current_email)
        
        return {"grounded_response": grounded_response}

    def write_draft_email(self,graphstate) -> GraphState:
        """Writes a draft email based on the current email and retrieved information."""
        print("Writing draft email...\n")
        grounded = graphstate.get("grounded_response", "")
        inputs = (
            f'# EMAIL CATEGORY: {graphstate["category"]}\n\n'
            f'# EMAIL TONE: {graphstate["tone"]}\n\n'
            f'# EMAIL CONTENT: \n{graphstate["current_email"].body}\n\n'
            f'# GROUNDED RESPONSE: \n{grounded}' 
        )
        
        writer_messages = graphstate.get('writer_messages', [])

        draft_result = self.agents.email_writer.invoke({
            "email_information": inputs,
            "history": writer_messages
        })

        email_draft = draft_result.email
        attempts = graphstate.get('attempts', 0) + 1

        writer_messages.append(f"Draft {attempts}:\n{email_draft}")

        return {
            "generated_email": email_draft, 
            "attempts": attempts,
            "writer_messages": writer_messages
        }

    def verify_generated_email(self,graphstate) -> GraphState:
        """Verifies the generated email using the proofreader agent."""
        print("Verifying generated email...\n")
        review = self.agents.email_proofreader.invoke({
            "email":graphstate["current_email"].body,
            "category": graphstate["category"],
            "tone": graphstate["tone"],
            "grounded_response": graphstate["grounded_response"],
            "generated_email":graphstate["generated_email"],
        })

        writer_messages =graphstate.get('writer_messages', [])
        writer_messages.append(f" Proofreader Feedback: \n{review.feedback}")

        return {
            "send": review.send,
            "writer_messages": writer_messages
        }

    def must_rewrite(self,graphstate) -> str:
        """Determines if the email needs to be rewritten based on the review and trial count."""
        email_sendable =graphstate["send"]
        if email_sendable:
            print("Email is good, ready to be sent!!!")
            graphstate["emails"].pop()
            graphstate["writer_messages"] = []
            return "send"
        elif graphstate["attempts"] >= 3:
            print("Email drafting failed - reached max attempts!")
            graphstate["emails"].pop()
            graphstate["writer_messages"] = []
            return "stop"
        else:
            print("Email draft is not good, must be rewritten...")
            return "rewrite"

    def create_draft_response(self,graphstate) -> GraphState:
        """Creates a draft response in Gmail."""
        print("Creating draft email...\n")
        self.gmail_tools.create_draft_reply(graphstate["current_email"],graphstate["generated_email"])
        
        return {"attempts": 0}

    def send_email_response(self,graphstate) -> GraphState:
        """Sends the email response directly using Gmail."""
        print("Sending email...\n")
        self.gmail_tools.send_reply(graphstate["current_email"],graphstate["generated_email"])
        
        return {"attempts": 0}
    
    def skip_unrelated_email(self,graphstate):
        """Skip unrelated email and remove from emails list."""
        print("Skipping unrelated email...\n")
        graphstate["emails"].pop()
        return graphstate