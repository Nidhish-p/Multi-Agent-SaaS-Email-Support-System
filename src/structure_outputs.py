from pydantic import BaseModel, Field
from typing import List

# Email classification output
class EmailCategoryOutput(BaseModel):
    category: str = Field(
        ...,
        description="Must be one of: feature_query, pricing_upgrade, downgrade_cancellation, onboarding_help, technical_support,other."
    )

# RAG query output
class RAGQueriesOutput(BaseModel):
    queries: List[str] = Field(
        ...,
        description="List of up to three questions/queries representing the customer's request."
    )

# Email writer output
class WriterOutput(BaseModel):
    email: str = Field(
        ...,
        description="The drafted follow up email."
    )

# Proof-reader output
class ProofReaderOutput(BaseModel):
    feedback: str = Field(
        ...,
        description="Explanation of whether the email is sendable."
    )
    send: bool = Field(
        ...,
        description="True if email is validated to be sent, else False."
    )