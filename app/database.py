from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config.config import BaseConfig

config = BaseConfig()

engine = create_engine(
    config.get("SQLALCHEMY_DATABASE_URI"), connect_args={"check_same_thread": False}
)
DB = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)
