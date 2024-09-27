from db import SessionLocal


def get_db():
    """ connection to sqlite database """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


