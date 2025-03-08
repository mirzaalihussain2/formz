from pydantic import BaseModel, field_validator, HttpUrl
from datetime import date

class BasicInfo(BaseModel):
    website: HttpUrl
    budget: float
    start_date: date
    end_date: date
    
    @field_validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values.data and v < values.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v