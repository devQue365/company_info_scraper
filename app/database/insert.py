from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
from app.database.database import sessionLocal, init_db, Base
from sqlalchemy.orm import Session
import torch
import re
import json
import random
# initialize the database
init_db()
db: Session = sessionLocal

# global seed settings
random.seed(101)
np.random.seed(101)
torch.manual_seed(101)
torch.use_deterministic_algorithms(True)

# we will be using 'all-MiniLM-L6-v2' sentence transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_model.eval()

def normalize_text(text):
    '''Lowercase, strip, and remove punctuation for consistent embeddings.'''
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    return text

def encode_text_to_vector(text: str, embed_model: SentenceTransformer):
    vec = embed_model.encode(text)
    return vec / np.linalg.norm(vec)  # we will be normalizing manually


# now, we will be implementing insertion operation
def generic_cache_insert(
    db: Session,
    model,
    param_list: list,
    param_values: list,
    embedding_field: str = 'embedded_data',
    embedding_model: SentenceTransformer = embedding_model,
) -> True | False:
    ''' Returns True if it is required to insert record in cache table or else False given that the record aldready exists '''
    text = " | ".join(
        f"{k}: {normalize_text(str(v))}" for k, v in zip(param_list, param_values)
    )
    vec = encode_text_to_vector(text, embedding_model)

    # First let us check if the record exists
    filters = {param: value for param, value in zip(param_list, param_values)}
    if db.query(model).filter_by(**filters).first():
        print("Already exists.")
        return False

    # insert the record in perch table
    entry = model(
        **filters,
        **{embedding_field: json.dumps(vec.tolist())}
    )
    db.add(entry)
    db.commit()
    return True



def generic_insert(
        db: Session,
        model,
        param_list: list,
        param_values: list,
):
    entry = model(
        **{param: value for param,value in zip(param_list, param_values)},
    )
    db.add(entry)
    db.commit()


def generic_delete(
    db: Session,
    model,
    param_list: list,
    param_values: list,
):
    # create a filter dictionary
    filter_kwargs = {param: value for param, value in zip(param_list, param_values)}
    # query and delete
    db.query(model).filter_by(**filter_kwargs).delete()
    db.commit()

def delete_table(model, engine):
    model.__table__.drop(engine, checkfirst = True)

def generic_delete_all(db, model):
    db.query(model).delete()

def delete_all_tables(engine):
    Base.metadata.drop_all(bind=engine)