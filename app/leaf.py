from sqlalchemy.orm import Session
from app.database import init_db, sessionLocal
from app.models import *
from datetime import datetime

# Initialize the database
init_db()

# create a database session
db : Session = sessionLocal()


# created the instances / records of external APIs which we are using in our app (providers -> alias -> p)

def tweet_init_leaf(db: Session):
    # This function is used to initialize the Tweet API usage table
    # It is called when the app starts to ensure that the table is ready for use
    # We will create a record for each provider we are using in our app
    # first provider : twttr API
    if db.query(TWT).count() == 0:
        p1 = TWT(
            name =  'twt__1',
            provider = 'twttr_API',
            used_calls = 0,
            total_calls = 500,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        p2 = TWT(
            name =  'twt__2',
            provider = 'Twitter_API_unofficial',
            used_calls = 0,
            total_calls = 1000,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        p3 = TWT(
            name =  'twt__3',
            provider = 'Twitter_AIO',
            used_calls = 0,
            total_calls = 300,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        p4 = TWT(
            name =  'twt__4',
            provider = 'Old_Bird_V1',
            used_calls = 0,
            total_calls = 500,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        # add the records to the sessions
        db.add(p1)
        db.add(p2)
        db.add(p3)
        db.add(p4)
        # save the changes
        db.commit()
        # close the session
        db.close()
    else: pass

def map_init_leaf(db: Session):
    # This function is used to initialize the MAP API usage table
    # It is called when the app starts to ensure that the table is ready for use
    # We will create a record for each provider we are using in our app
    if db.query(MAP).count() == 0:
        p1 = MAP(
            name =  'gm__1',
            provider = 'Google_Map_Places',
            used_calls = 0,
            total_calls = 100,
            reset_type = 'D', # monthly
            last_reset = datetime.now()
            )
        p2 = MAP(
            name =  'gm__2',
            provider = 'Google_Map_Scraper',
            used_calls = 0,
            total_calls = 1000,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        p3 = MAP(
            name =  'gm__backup',
            provider = 'Google_Place_Autocomplete_and_Place_Info_API',
            used_calls = 0,
            total_calls = 1000,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        # add the records to the sessions
        db.add(p1)
        db.add(p2)
        db.add(p3)
        # save the changes
        db.commit()
        # close the session
        db.close()  
    else: pass

def salary_init_leaf(db: Session):
    # This function is used to initialize the Salary API usage table
    # It is called when the app starts to ensure that the table is ready for use
    # We will create a record for each provider we are using in our app
    if db.query(SAL).count() == 0:
        p1 = SAL(
            name =  'gd__1',
            provider = 'glassdoor_V1',
            used_calls = 0,
            total_calls = 100,
            reset_type = 'M', # monthly
            last_reset = datetime.now(),
            type = 'E',  # for estimated salary data
            confidence = 0  # confidence score for salary data
            )
        p2 = SAL(
            name =  'gd__2',
            provider = 'glassdoor_V2',
            used_calls = 0,
            total_calls = 100,
            reset_type = 'M', # monthly
            last_reset = datetime.now(),
            type = 'E',  # for estimated salary data
            confidence = 1  # confidence score for salary data
            )
        p3 = SAL(
            name =  'js',
            provider = 'jsearch_API',
            used_calls = 0,
            total_calls = 200,
            reset_type = 'M', # monthly
            last_reset = datetime.now(),
            type = 'E',  # for estimated salary data
            confidence = 1  # confidence score for salary data
            )
        p4 = SAL(
            name =  'jsd',
            provider = 'jobsalarydata',
            used_calls = 0,
            total_calls = 50,
            reset_type = 'M', # monthly
            last_reset = datetime.now(),
            type = 'E',  # for estimated salary data
            confidence = 1  # confidence score for salary data
            )
        p5 = SAL(
            name =  'cj',
            provider = 'careerjet',
            used_calls = 0,
            total_calls = 1000,
            reset_type = 'H', # hourly
            last_reset = datetime.now(),
            type = 'L',  # for listing based salary data
            confidence = 1  # confidence score for salary data
            )
        # add the records to the sessions
        db.add(p1)
        db.add(p2)
        db.add(p3)
        db.add(p4)
        db.add(p5)
        # save the changes
        db.commit()
        # close the session
        db.close()
    else: pass

def overview_init_leaf(db: Session):
    # This function is used to initialize the Overview API usage table
    # It is called when the app starts to ensure that the table is ready for use
    # We will create a record for each provider we are using in our app
    if db.query(OVR).count() == 0:
        p1 = OVR(
            name =  'ov__1',
            provider = 'Real_time_GD_Apyflux',
            used_calls = 0,
            total_calls = 300,
            reset_type = 'M', # monthly
            last_reset = datetime.now()
            )
        # add the records to the sessions
        db.add(p1)
        # save the changes
        db.commit()
        # close the session
        db.close()
    else: pass


