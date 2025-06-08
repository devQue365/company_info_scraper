from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

# create a base class for our table
Base = declarative_base()

# Tweet API usage table
class TWT(Base):
    __tablename__ = "TWT__USAGE"
    Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)

# Maps API usage table
class MAP(Base):
    __tablename__ = "MAP__USAGE"
    Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)

# Salary API usage table
class SAL(Base):
    __tablename__ = "SAL__USAGE"
    Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)
    type = Column(String, default= 'E', nullable = False)  # type of salary data (e.g., hourly, annual)
    confidence = Column(Integer, default = 0)  # confidence score for salary data

# Overview API usage table
class OVR(Base):
    __tablename__ = "OVR__USAGE"
    Id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, nullable = False)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)

# Table to hold glassdoor ids
class GD_CRED(Base):
    __tablename__ = "GD__CRED"
    Id = Column(Integer, index = True)
    company_name = Column(String, unique = True, nullable = False)
    company_id = Column(String, unique = True, primary_key = True, nullable = False)
    location_id = Column(String, unique = True, nullable = False)
