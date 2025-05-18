# For handling request model
from pydantic import BaseModel

class InfoRequest(BaseModel):
    company_name : str
    job_title : str