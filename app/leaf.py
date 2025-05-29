from sqlalchemy.orm import Session
from database import init_db, sessionLocal
from models import ApiUsageTable
from datetime import datetime

# Initialize the database
init_db()

# create a database session
db : Session = sessionLocal()

# created the instances / records of external APIs which we are using in our app (providers -> alias -> p)

# first provider : Jsearch
p1 = ApiUsageTable(
    provider = 'jsearch',
    used_calls = 0,
    total_calls = 200,
    reset_type = 'M', # monthly
    last_reset = datetime.now()
)

p2 = ApiUsageTable(
    provider = 'glassdoor',
    used_calls = 0,
    total_calls = 200,
    reset_type = 'M', # monthly
    last_reset = datetime.now()
)

p3 = ApiUsageTable(
    provider = 'jobsalarydata',
    used_calls = 0,
    total_calls = 50,
    reset_type = 'M', # monthly
    last_reset = datetime.now()
)

p4 = ApiUsageTable(
    provider = 'careerjet',
    used_calls = 0,
    total_calls = 1000,
    reset_type = 'H', # hourly
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



