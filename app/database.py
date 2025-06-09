from sqlalchemy import create_engine
# sessionmaker is like a factory for making sessions i.e. miniconnections to the database
from sqlalchemy.orm import sessionmaker
from app.models import Base

# We will be creating a SQLite engine & the database file will be 'app.db'
db_url = 'sqlite:///./app/app.db'
# note here: sqlite -> sqlite engine, :/// -> relative path, ./app.db -> database file

engine = create_engine(db_url, connect_args={'check_same_thread': False}) # connect to the database

# let's create a session
sessionLocal = sessionmaker(
    autocommit = False, # we must explicitly save the changes
    autoflush = False, # SQLAlchemy won't autosend changes untill we specify it to do so
    bind = engine # binds to sqlite database engine
)

# initialize the database
def init_db():
    # create tables in the database if they don't exist
    Base.metadata.create_all(bind = engine)

# Function to start database session
def start_db_session():
    db_session = sessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
