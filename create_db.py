import os
from g_login import db, User
from sqlalchemy import create_engine
basedir = os.path.abspath(os.path.dirname(__file__))

engine = create_engine('sqlite:///' + os.path.join(basedir, "test.db"), echo=False)
User.__table__.drop(engine)
db.create_all()

