from pydantic import BaseModel


class SQSMessage(BaseModel):
    body: str
    timestamp: int
    receipt_handle: str