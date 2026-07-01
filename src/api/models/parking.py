from pydantic import BaseModel, Field

# Cererea pentru activarea unui abonament
class ParkingFeeResponse(BaseModel):
    parking_code: str
    parked_minutes: int = Field(ge=0)
    billable_minutes: int = Field(ge=0)
    amount: float = Field(ge=0)
    currency: str = "RON"

# Cererea pentru plata parcarii
class ParkingPaymentRequest(BaseModel):
    parking_code: str = Field(min_length=1, max_length=20)
    expected_amount: float = Field(ge=0)

# Raspunsul pentru plata parcarii
class ParkingPaymentResponse(BaseModel):
    paid: bool
    parking_code: str
    amount: float
    currency: str = "RON"
    message: str
