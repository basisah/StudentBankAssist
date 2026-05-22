#to make sure every field is validated and to define the types of the data we are working with, we can use pydantic models

from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

def ChatRequest(BaseModel):
    model_config = ConfigDict(strip_whitespace=True)
    session_id: str
    message: str

    @field_validator("message")
    def message_must_not_be_empty(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Message is too short")
        if len(v) > 1000:
            raise ValueError("Message is too long")
        return v
    

def Source(BaseModel):
    document: str
    metadata: dict

def ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: list[Source]
    escalate: bool
    timestamp: datetime = datetime.now()

def EscalateRequest(BaseModel):
    session_id: str
    reason: Optional[str] = None


def EscalateResponse(BaseModel):
    message: str

def Product_Info(BaseModel):
    name: str
    category: str
    description: str