from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


base = declarative_base()

engine_lite = create_engine ("postgresql+psycopg2://postgres:123456789@127.0.0.1:5432/db_horizon")

def dbsession():
    Session = sessionmaker(bind = engine_lite)
    session = Session()
    return session 
