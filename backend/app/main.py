from fastapi import FastAPI
# take the class FastAPI from the "fastapi" package
from pydantic import BaseModel

app = FastAPI()
# create an application object. name matters, as the start command refers to it

notes = []

class CreateNoteRequest(BaseModel):
    text: str

@app.get("/api/notes")
# decorator: it registers the function below as a handler for GET method, path '/api/notes'
def list_notes():
    return notes

@app.post("/api/notes", status_code=201)
# register POST method handler, set custom success code to 201
def create_note(request_body: CreateNoteRequest) -> dict:
    new_note = {"id": len(notes) + 1, "text": request_body.text}
    notes.append(new_note)
    return new_note






