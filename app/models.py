import json


from sqlalchemy import Column, Integer, Unicode


from app.database import Base, engine, DBSession


class AuthorizableAttribute(Base):
    aaid = Column(Integer, primary_key=True, index=True)
    authorizable_attribute_id = Column(Unicode, unique=True, index=True)
    authorizable_attribute_info = Column(Unicode)

    @classmethod
    def by_aa_id(cls, aa_id):
        return DBSession.query(cls).filter_by(authorizable_attribute_id=aa_id).first()

    @property
    def value_set(self):
        aa_info = json.loads(self.authorizable_attribute_info)
        return set([(k, v) for _ in aa_info for k, v in _.items()])

    def value_by_name(self, name):
        info = json.loads(self.authorizable_attribute_info)
        info = [json.loads(_) for _ in info]
        return next((i for i in info if i["name"] == name), None)

    def value_is_valid(self, name, value):
        info = self.value_by_name(name)
        if not info:
            return False

        return value in info["valid_values"]


Base.metadata.create_all(bind=engine)


def init_models(_engine):
    Base.metadata.create_all(bind=_engine)
