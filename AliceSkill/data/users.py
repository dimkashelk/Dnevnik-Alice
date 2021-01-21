import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    token = sqlalchemy.Column(sqlalchemy.String, default=None)
    role = sqlalchemy.Column(sqlalchemy.String, default=None)
    authorized = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    school_id = sqlalchemy.Column(sqlalchemy.String, default=None)
    edu_group = sqlalchemy.Column(sqlalchemy.String, default=None)
    person_id = sqlalchemy.Column(sqlalchemy.String, default=None)

