from pydantic import BaseModel


class GenerateResponse(BaseModel):
    message: str
    midi_file: str