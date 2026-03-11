from pydantic import BaseModel, Field
from typing import List

# Email classification output
class EmailCategoryToneOutput(BaseModel):
    category: str = Field(
        ...,
        description="Must be one of: feature_query, pricing_upgrade, downgrade_cancellation, onboarding_help, technical_support,other."
    )
    tone: str = Field(
        ...,
        description="Must be one of: neutral_inquiry, potential_buyer, frustrated, urgent, churn_signal, confused"
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