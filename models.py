from database import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True)
    username = Column(String(50),unique=True)
    firstname = Column(String(50))
    lastname = Column(String)
    hashed_password = Column(String)


class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    states = relationship("State", back_populates="region")



class State(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    state_capital = Column(String)
    region_id = Column(Integer, ForeignKey('regions.id'))
    region = relationship("Region", back_populates="states")
    lgas = relationship("LGA", back_populates="state")


class LGA(Base):
    __tablename__ = 'lgas'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    state_id = Column(Integer, ForeignKey('states.id'))
    state = relationship("State", back_populates="lgas")