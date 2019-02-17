import json

from sqlalchemy import Column, Integer, Unicode

from app.database import Base, engine, DB


class AuthorizableAttribute(Base):
    aaid = Column(Integer, primary_key=True, index=True)
    authorizable_attribute_id = Column(Unicode, unique=True, index=True)
    authorizable_attribute_info = Column(Unicode)

    @classmethod
    def by_aa_id(cls, aa_id):
        return DB.query(cls).filter_by(authorizable_attribute_id=aa_id).first()

    @property
    def value_set(self):
        aa_info = json.loads(self.authorizable_attribute_info)
        return set([(k, v) for _ in aa_info for k, v in _.items()])


Base.metadata.create_all(bind=engine)


def init_models(_engine):
    Base.metadata.create_all(bind=_engine)
