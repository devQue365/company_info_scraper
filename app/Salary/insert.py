from sentence_transformers import SentenceTransformer
import numpy as np
from app.database.models import CACHE_SAL
from app.database.database import sessionLocal, init_db
from sqlalchemy.orm import Session
# initialize the database
init_db()
db: Session = sessionLocal

# we will be using 'all-MiniLM-L6-v2' sentence transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# first of all we want to get text from parameters like (abc, devops, new york) -> "abc devops newyork" [lowercased]
def getTextFromParams(company_name: str, job_title: str, location: str):
    return f"{company_name} {job_title} {location}".lower()

# now, we also want a helper function to convert vector object back to string object
def getStringFromVector(vec):
    return ','.join(map(str, vec))

# now, we will be implementing insertion operation
def salary_cache_insert(company_name: str, job_title: str, location: str, salary_data: dict, type: str, confidence: int, db: Session):
    # first check the salary data
    if(type == 'E' and confidence == 1):
        # get the text form of params
        text_params = getTextFromParams(company_name, job_title, location)
        # embed the textual information to vector format
        vec = embedding_model.encode(text_params)
        # create a new entry
        entry = CACHE_SAL(
            company_name = company_name.lower(),
            job_title = job_title.lower(),
            location = location.lower(),
            salary_data = salary_data,
            embedded_data = getStringFromVector(vec)
        )
        db.add(entry)
        db.commit()
    return

