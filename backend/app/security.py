from flask_security import SQLAlchemyUserDatastore

from app.extensions import db
from app.models import Role, User


user_datastore = SQLAlchemyUserDatastore(db, User, Role)