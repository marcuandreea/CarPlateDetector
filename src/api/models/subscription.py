from pydantic import BaseModel, Field

# Cererea pentru activarea unui abonament
class SubscriptionActivateRequest(BaseModel):
    subscription_id: int = Field(..., gt=0)
