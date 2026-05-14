from sqlalchemy.orm import Session


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    @classmethod
    def get_by_id(cls, db_session: Session, id):
        if any(
                (isinstance(id, str) and id.isdigit(),
                 isinstance(id, (int, float))),
        ):
            return db_session.query(cls).get(int(id))
        return None

    @classmethod
    def get_by_name(cls, db_session: Session, value, unique_field="name"):
        query_attribute = getattr(cls, unique_field)
        result = db_session.query(cls).filter(query_attribute == value).one_or_none()
        return result

    @classmethod
    def get_all(cls, db_session: Session):

        return db_session.query(cls).all()

    @classmethod
    def create(cls, db_session: Session, **kwargs):
        instance = cls(**kwargs)
        return instance.save(db_session)

    def update(self, db_session: Session, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save(db_session) or self

    def save(self, db_session: Session, commit=True):
        db_session.add(self)
        if commit:
            db_session.commit()
        return self

    def flush(self, db_session: Session):
        db_session.add(self)
        db_session.flush()
        return self

    def delete(self, db_session: Session, commit=True):
        db_session.delete(self)
        return commit and db_session.commit()
