from pydantic import BaseModel


class Truth(BaseModel):
    id: str
    truth: str
    category: str
    weight: str
