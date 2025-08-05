from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: any
    __name__: str
    # This function automatically generates a table name
    # from the class name (e.g., class Candidate -> table candidates)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"