from pydantic import BaseModel, Field
from typing import List, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Optional

class Email(BaseModel):
    id: str = Field(..., description="UID of the email")
    threadId: str = Field(..., description="Thread id of the email")
    messageId: str = Field(..., description="Message id of the email")
    references: Optional[str]  = Field( None, description="References of the email")
    sender: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Body of the email")
    
class GraphState(TypedDict):
    status : str
    emails: List[Email]
    current_email: Email
    is_spam : str
    category: str
    tone: str
    generated_email: str
    grounded_response: str
    writer_messages: Annotated[list, add_messages]
    send: bool
    attempts: int