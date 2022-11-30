from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2.extras


from service_provider_api.config import settings


# need to call this
# before working with UUID objects in PostgreSQL
psycopg2.extras.register_uuid()

# Configure some constants for the database
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
