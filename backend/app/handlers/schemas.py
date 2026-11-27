from datetime import datetime

# PositiveInt = pydantic type "int that must be > 0" (pydantic = validation library used by FastAPI)
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

# Upper limit of ids in one batch request, so one call cannot hold the database too long
MAX_BATCH_SIZE = 100


class NoteRequest(BaseModel):
    """Body of create and update requests: the text of a note."""

    text: str


class NoteOut(BaseModel):
    """One note as the API shows it to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime


class NoteIn(BaseModel):
    """Body of create and update requests: the text of a note"""

    text: str


class BatchDeleteRequest(BaseModel):
    """Body of POST /api/notes/batch-delete: ids of the notes to delete in one transaction."""

    ids: list[PositiveInt] = Field(min_length=1, max_length=MAX_BATCH_SIZE)
    # list[PositiveInt] = JSON array where every item is an integer > 0
    # Field(min_length=1) = list must not be empty
    # Field(max_length=MAX_BATCH_SIZE) = list must not be longer than the limit
