from pydantic import BaseModel
from typing import List, Dict, Any

class FilterItem(BaseModel):
    id: str | int
    name: str

class FilterResponse(BaseModel):
    cities: List[str]
    work_types: List[FilterItem]
    domains: List[FilterItem]