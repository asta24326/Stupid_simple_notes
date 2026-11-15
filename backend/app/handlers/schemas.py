from datetime import datetime
from pydantic import BaseModel, ConfigDict

class NoteRequest(BaseModel):
    """Body of create and update requests: the text of a note"""

    text: str

class NoteResponse(BaseModel):
    """A note as the API shows it to clients"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
