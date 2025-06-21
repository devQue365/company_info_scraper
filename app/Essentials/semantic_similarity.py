from sentence_transformers import SentenceTransformer
import numpy as np
from app.database.models import CACHE_SAL
from app.database.database import sessionLocal, init_db
from sqlalchemy.orm import Session
import re
import torch
import json

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

def encode_text_to_vector(text: str, embed_model: SentenceTransformer):
    vec = embed_model.encode(text)
    return vec / np.linalg.norm(vec)  # we will be normalizing manually


def normalize_text(text):
    '''Lowercase, strip, and remove punctuation for consistent embeddings.'''
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    return text

# now, main logic to perform semantic matching based on user inputted args
def semantic_match(
    db: Session,
    model,
    param_names: list,
    param_values: list,
    embedding_field: str = 'embedded_data',
    threshold: float = 0.65,
    embedding_model: SentenceTransformer = embedding_model
):
    text = " | ".join(
        f"{k}: {normalize_text(str(v))}" for k, v in zip(param_names, param_values)
    )
    ip_vec = encode_text_to_vector(text, embedding_model)

    records = db.query(model).all()
    results = []
    for rec in records:
        try:
            stored_vec = np.array(json.loads(getattr(rec, embedding_field)))
            sim = cosine_similarity(ip_vec, stored_vec)
            results.append((rec, sim))
        except Exception as e:
            print(f"Invalid embedding in record {rec.Id}: {e}")

    if not results:
        return None

    # get best match
    best_match = max(results, key=lambda x: x[1])
    if best_match[1] >= threshold:
        return best_match[0]
    return None
