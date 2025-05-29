from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

# create a base class for our table
Base = declarative_base()

# created a table to keep a record of API usage
class ApiUsageTable(Base):
    __tablename__ = "API_USAGE_DATA"
    Id = Column(Integer, primary_key = True, index = True)
    provider = Column(String, unique = True, nullable = False)
    used_calls = Column(Integer, default = 0)
    total_calls = Column(Integer, nullable = False)
    reset_type = Column(String, nullable = False)
    # We have to store a time stamp value for last reset
    last_reset = Column(DateTime, nullable = False)
