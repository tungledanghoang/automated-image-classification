from pydantic import BaseModel


class SQSMessage(BaseModel):
    body: dict
    timestamp: int
    receipt_handle: str


class SQSSendMessage(BaseModel):
    status: str
    bucket: str
    key: str
    result: str
