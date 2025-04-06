from pydantic import BaseModel, field_validator


class RawNotes(BaseModel):
    pitch: float
    step: float
    duration: float

class GenerateRequest(BaseModel):
    start_notes: list[RawNotes] | None = None
    num_predictions: int
    temperature: float
    tempo: int

    @field_validator('temperature')
    def validate_temperature(cls, v):
        if not 0 < v <= 2:
            raise ValueError('Температура має бути в діапазоні (0, 2]')
        return v
    
    @field_validator('num_predictions')
    def validate_num_predictions(cls, v):
        if not 0 < v:
            raise ValueError('Кількість нот має бути додатня')
        return v
    
    @field_validator('tempo')
    def validate_tempo(cls, v):
        if not 0 < v <= 400:
            raise ValueError('Темп має бути додатня')
        return v