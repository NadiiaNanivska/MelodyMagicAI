from pydantic import BaseModel


class RawNotes(BaseModel):
    pitch: float
    step: float
    duration: float

class GenerateRequest(BaseModel):
    start_notes: list[RawNotes] | None = None
    num_predictions: int
    temperature: float
    tempo: int