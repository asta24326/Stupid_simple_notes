from pydantic import BaseModel

class CreateNoteRequest(BaseModel):
    text: str
    
