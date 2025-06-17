from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func, CHAR, event, MetaData
from sqlalchemy.ext.declarative import declarative_base

# create a base class for our table
Base = declarative_base()

# Tweet API usage table
class TWT(Base):
    __tablename__ = "TWT__USAGE"
    # Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, primary_key = True, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)
    token_id = Column(String, default = 'TWT', nullable = False)


# Maps API usage table
class MAP(Base):
    __tablename__ = "MAP__USAGE"
    # Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, primary_key = True, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)
    token_id = Column(String, default = 'MAP', nullable = False)


# Store company's overview (static in nature)
class CACHE_MAP(Base):
    __tablename__ = "CACHE__MAP"
    company_name = Column(String, primary_key = True)
    location = Column(String, nullable = False)
    location_data = Column(JSON)
    reset_type = Column(CHAR, default = 'M', nullable = False) # monthly reset
    last_reset = Column(DateTime, default = func.now())
    embedded_data = Column(Text)  # we will be adding a comma sperated vector in this column



# Salary API usage table
class SAL(Base):
    __tablename__ = "SAL__USAGE"
    # Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, primary_key = True, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)
    type = Column(String, default= 'E', nullable = False)  # type of salary data (e.g., hourly, annual)
    confidence = Column(Integer, default = 0)  # confidence score for salary data
    token_id = Column(String, default = 'SAL', nullable = False)

# Store company's salary estimation
# only estimated and confident data will be allowed
class CACHE_SAL(Base):
    __tablename__ = "CACHE__SAL"
    Id = Column(Integer, primary_key = True, index = True)
    company_name = Column(String, nullable = False)
    job_title = Column(String, nullable = False)
    location = Column(String, nullable = False)
    # store the salary data (json format)
    salary_data = Column(JSON)
    reset_type = Column(CHAR, default= 'W', nullable = False) # weekly reset
    last_reset = Column(DateTime, default = func.now())
    embedded_data = Column(Text)  # we will be adding a comma sperated vector in this column




# Overview API usage table
class OVR(Base):
    __tablename__ = "OVR__USAGE"
    # Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, primary_key = True, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)
    token_id = Column(String, default = 'OVR', nullable = False)

# Store company's overview (static in nature)
class CACHE_OVR(Base):
    __tablename__ = "CACHE__OVR"
    company_name = Column(String, primary_key = True)
    company_overview = Column(JSON)
    reset_type = Column(CHAR, default = 'M', nullable = False) # monthly reset
    last_reset = Column(DateTime, default = func.now())




# create them
# Base.metadata.create_all(bind = None)
# alembic revision --autogenerate -m "Added embedded_data column in CACHE__MAP"
# alembic upgrade head