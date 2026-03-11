from src.workflow import Workflow
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# config 
config = {'recursion_limit': 100}

workflow = Workflow()
app = workflow.app

initial_state = {
    "emails": [],
    "current_email": {
      "id": "",
      "threadId": "",
      "messageId": "",
      "references": "",
      "sender": "",
      "subject": "",
      "body": ""
    },
    "email_category": "",
    "generated_email": "",
    "rag_queries": [],
    "retrieved_documents": "",
    "writer_messages": [],
    "sendable": False,
    "trials": 0
}

# Run the Saas Email orchestration System
for output in app.stream(initial_state, config):
    for key, value in output.items():
        print(f"Finished running: {key}:")


