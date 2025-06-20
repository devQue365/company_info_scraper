from sentence_transformers import SentenceTransformer
import numpy as np
from app.database.models import CACHE_SAL
from app.database.database import sessionLocal, init_db
from sqlalchemy.orm import Session
import re
import torch

# initialize the database
init_db()
db: Session = sessionLocal

# get the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_model.eval()

# cosine similarity to check whether the two vectors are pointing roughly in the same direction
def cosine_similarity(vec1, vec2):
    # return cos(theeta) =  (a.b)/(|a|.|b|)
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec2))

def string_to_vector(text: str):
    '''Converts comma separated vector string into a numpy array.'''
    return np.array(list(map(float, text.split(','))))

def normalize_text(text):
    '''Lowercase, strip, and remove punctuation for consistent embeddings.'''
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    return text

# now, main logic to perform semantic matching based on user inputted args
def semantic_match(
        db: Session,
        model, # the ORM model to be used
        param_names = [], # list of parameter names
        param_values = [], # list of parameter values
        embedding_field: str = 'embedded_data',
        threshold: float = 0.7
    ) -> object:
    # step_1: Combine the parameters into a single string to be used for embedding
    param_text_format = " | ".join(
        f"{name}: {normalize_text(str(value))}" for name, value in zip(param_names, param_values)
    )
    print("param_text_format:", param_text_format)
    # encode the stored vector using embedding model
    with torch.no_grad():
        ip_param_vec = embedding_model.encode(param_text_format, normalize_embeddings=True)

    # retreive all the records from cache storage
    records = db.query(model).all()
    # iterate through each record and check for semantic match
    for record in records:
        # get the embedded vector
        stored_param_vector = string_to_vector(getattr(record, embedding_field))
        # check for cosine similarity -> whether they are pointing in the same direction or not
        cos_similarity = cosine_similarity(ip_param_vec, stored_param_vector)
        # compare with threshold value (default = 0.85)
        if(cos_similarity >= threshold):
            return record
    return None