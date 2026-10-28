from pydantic import BaseModel
from typing import List, Dict, Any

class JobSchema(BaseModel):
    source: str
    slug: str
    title: str
    company: str | None = None
    salary: str | None = None
    estimated_salary: str | None = None
    work_type: str | None = None
    experience_level: str | None = None
    city: str | None = None
    domain: str | None = None
    required_skills: str | None = None
    ad_link: str | None = None
