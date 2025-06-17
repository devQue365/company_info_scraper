from sentence_transformers import SentenceTransformer
import numpy as np
from app.database.models import CACHE_SAL
from app.salary.insert import getStringFromVector, getTextFromParams
from app.database.database import sessionLocal, init_db
from sqlalchemy.orm import Session

# initialize the database
init_db()
db: Session = sessionLocal

# get the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# cosine similarity to check whether the two vectors are pointing roughly in the same direction
def cosine_similarity(vec1, vec2):
    # return the cosine angle (a.b)/(|a|.|b|)
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec2))


def string_to_vector(text: str):
    '''Converts comma separated vector string into a numpy array.'''
    return np.array(list(map(float, text.split(','))))

# Now, main logic to perform semantic matching based on user inputted args
def semantic_match(company_name, job_title, location, db: Session, threshold: float = 0.85) -> dict:
    # convert to text format
    param_text_format = getTextFromParams(company_name, job_title, location)
    # encode the stored vector using embedding model
    ip_param_vec = embedding_model.encode(param_text_format)

    # retreive all the records from cache storage
    records = db.query(CACHE_SAL).all()
    # iterate through each record and check for semantic match
    for record in records:
        # get the embedded vector
        stored_param_vector = string_to_vector(record.embedded_data)
        # check for cosine similarity -> whether they are pointing in the same direction or not
        cos_similarity = cosine_similarity(ip_param_vec, stored_param_vector)
        # compare with threshold value (default = 0.85)
        if(cos_similarity >= threshold):
            return {
                'company_name': record.company_name,
                'job_title': record.job_title,
                'location': record.location
            }
        return None