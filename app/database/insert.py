from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
from app.database.models import CACHE_SAL
from app.database.database import sessionLocal, init_db
from sqlalchemy.orm import Session
# initialize the database
init_db()
db: Session = sessionLocal

# we will be using 'all-MiniLM-L6-v2' sentence transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# first of all we want to get text from parameters like (abc, devops, new york) -> "abc devops newyork" [lowercased]
def getTextFromParams(param_values):
    # return f"{company_name} {job_title} {location}".lower()
    return " ".join(str(v).lower() for v in param_values)

# now, we also want a helper function to convert vector object back to string object
def getStringFromVector(vec):
    return ','.join(map(str, vec))

# now, we will be implementing insertion operation
def generic_cache_insert(
        db: Session,
        model,
        param_list: list, # list of params
        param_values: list, # list of param values 
    ):
    # get the text form of params
    text_params = getTextFromParams(param_values)
    # embed the textual information to vector format
    vec = embedding_model.encode(text_params)
    # get the instance type from string
    # param_list = [lambda x: locals()[x] for x in param_list]
    # create a new entry
    entry = model(
        # assign values
        **{param: value for param, value in zip(param_list, param_values)},
        embedded_data = getStringFromVector(vec)
    )
    db.add(entry)
    db.commit()


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