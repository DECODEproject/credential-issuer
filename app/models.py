import json


from sqlalchemy import Column, Integer, Unicode, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship, backref

from app.database import Base, engine, DBSession


class AuthorizableAttribute(Base):
    aaid = Column(Integer, primary_key=True, index=True)
    authorizable_attribute_id = Column(Unicode, unique=True, index=True)
    authorizable_attribute_info = Column(Unicode, nullable=False)
    authorizable_attribute_info_optional = Column(Unicode, nullable=True)
    keypair = Column(Unicode)
    verification_key = Column(Unicode)
    reissuable = Column(Boolean, default=False, nullable=False)

    @classmethod
    def by_aa_id(cls, aa_id):
        return DBSession.query(cls).filter_by(authorizable_attribute_id=aa_id).first()

    def _find_value_by_name(self, name, data):
        info = json.loads(data)
        info = [json.loads(_) for _ in info]
        return next((i for i in info if i["name"] == name), None)

    def value_by_name(self, name):
        return self._find_value_by_name(name, self.authorizable_attribute_info)

    def value_option_by_name(self, name):
        return self._find_value_by_name(name, self.authorizable_attribute_info_optional)

    def optional_k(self, name):
        option = self.value_option_by_name(name)
        return option["k"]

    def value_is_valid(self, name, value):
        info = self.value_by_name(name)
        optional = self.value_option_by_name(name)
        is_optional = False
        if optional:
            is_optional = value in optional.get("value_set", [])
        return value in info["value_set"] or is_optional

    @property
    def value_names(self):
        aa_info = json.loads(self.authorizable_attribute_info)
        return [json.loads(_)["name"] for _ in aa_info]

    @property
    def value_name_type(self):
        aa_info = json.loads(self.authorizable_attribute_info)
        return [{json.loads(_)["name"]: json.loads(_)["type"]} for _ in aa_info]

    @property
    def optional_value_name_type(self):
        aa_info = json.loads(self.authorizable_attribute_info_optional)
        return [json.loads(_) for _ in aa_info]

    @property
    def optionals(self):
        optionals = json.loads(self.authorizable_attribute_info_optional)
        return [json.loads(_)["name"] for _ in optionals]

    def publish(self):
        return {
            "authorizable_attribute_id": self.authorizable_attribute_id,
            "authorizable_attribute_info": self.value_name_type,
            "authorizable_attribute_info_optional": self.optional_value_name_type,
            "verification_key": json.loads(self.verification_key),
            "reissuable": self.reissuable,
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

    @classmethod
    def total(cls):
        return DBSession.query(cls).count()


class Statistics(Base):
    uid = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode, nullable=False)
    value = Column(Unicode, nullable=False)
    aaid = Column(
        Unicode, ForeignKey("authorizableattribute.aaid"), index=True, nullable=False
    )
    authorizable_attribute = relationship(
        "AuthorizableAttribute", backref=backref("stats", cascade="all, delete-orphan")
    )

    @classmethod
    def aggregate(cls):
        result = {}
        values = (
            DBSession.query(cls.name, cls.value, func.count(cls.value), cls.aaid)
            .group_by(cls.name, cls.value)
            .all()
        )
        for v in values:
            existent_list = result.get(v[0], [])
            existent_list.append({v[1]: v[2]})
            aa = AuthorizableAttribute.by_aa_id(v[3])
            if v[2] >= aa.optional_k(v[0]):
                result[v[0]] = existent_list

        result["total"] = ValidatedCredentials.total()

        return result


Base.metadata.create_all(bind=engine)


def init_models(_engine):  # pragma: no cover
    Base.metadata.create_all(bind=_engine)
