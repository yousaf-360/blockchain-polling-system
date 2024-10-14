from pydantic import BaseModel, Field
from typing import List, Dict
import uuid
 
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    username: str
    password: str

class Poll(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    question: str
    options: Dict[str, int]  

    class Config:
        populate_by_name = True 

