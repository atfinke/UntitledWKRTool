import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class Page(Base):
    __tablename__ = 'page'

    url = Column(String, primary_key=True)
    views = Column(Integer)
    links_here = Column("links_here", ARRAY(String))

engine = create_engine('postgresql://localhost')
Base.metadata.create_all(engine)