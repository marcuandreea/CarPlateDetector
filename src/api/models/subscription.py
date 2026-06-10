from pydantic import BaseModel, Field

class SubscriptionActivateRequest(BaseModel):
    subscription_id: int = Field(..., gt=0)
