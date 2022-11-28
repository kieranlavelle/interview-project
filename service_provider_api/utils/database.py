from contextlib import contextmanager

from psycopg2 import connect
import psycopg2.extras


from service_provider_api.config import settings


# need to call this
# before working with UUID objects in PostgreSQL
psycopg2.extras.register_uuid()


@contextmanager
def get_connecton():
    conn = connect(settings.DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    yield conn
    conn.commit()
    conn.close()
