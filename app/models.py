import json


from sqlalchemy import Column, Integer, Unicode, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

from app.database import Base, engine, DBSession


class AuthorizableAttribute(Base):
    aaid = Column(Integer, primary_key=True, index=True)
    authorizable_attribute_id = Column(Unicode, unique=True, index=True)
    authorizable_attribute_info = Column(Unicode, nullable=False)
    keypair = Column(Unicode)
    verification_key = Column(Unicode)
    reissuable = Column(Boolean, default=False, nullable=False)

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

        return value in info["value_set"]

    @property
    def value_names(self):
        aa_info = json.loads(self.authorizable_attribute_info)
        return [json.loads(_)["name"] for _ in aa_info]

    @property
    def value_name_type(self):
        aa_info = json.loads(self.authorizable_attribute_info)
        return [{json.loads(_)["name"]: json.loads(_)["type"]} for _ in aa_info]

    def publish(self):
        return {
            "authorizable_attribute_id": self.authorizable_attribute_id,
            "authorizable_attribute_info": self.value_name_type,
            "verification_key": json.loads(self.verification_key),
        }


class ValidatedCredentials(Base):
    uid = Column(Integer, primary_key=True, index=True)
    value = Column(Unicode, index=True, nullable=False)
    aaid = Column(
        Unicode, ForeignKey("authorizableattribute.aaid"), index=True, nullable=False
    )
    authorizable_attribute = relationship(
        "AuthorizableAttribute",
        backref=backref("validated", cascade="all, delete-orphan"),
    )

    @classmethod
    def exists(cls, aaid, value):
        return (
            DBSession.query(cls)
            .filter_by(aaid=aaid)
            .filter_by(value=json.dumps(value))
            .first()
        )


Base.metadata.create_all(bind=engine)


def init_models(_engine):
    Base.metadata.create_all(bind=_engine)
