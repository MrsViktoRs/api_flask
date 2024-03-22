import pydantic
from typing import Optional


class CreatePosted(pydantic.BaseModel):
    title: str
    description: str
    owner: str


class UpdatePosted:
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
