from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Alert(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    created_at: datetime
    updated_at: datetime
    status: str

class Client(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CorrelationGroup(BaseModel):
    id: int
    name: str
    alerts: List[Alert]
    created_at: datetime
    updated_at: datetime