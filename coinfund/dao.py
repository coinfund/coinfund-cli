# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:18:53
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-01 16:50:27

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

# Base
Base = declarative_base()

class Investor(Base):
  """
  The investor model.
  """
  __tablename__ = 'investors'

  id          = Column(Integer, primary_key=True)
  first_name  = Column(String)
  last_name   = Column(String)

  def __repr__(self):
    return '<Investor %s %s>' % (self.first_name, self.last_name)

def connect(settings):
  engine = create_engine(settings['database_uri'], echo=False)
  Session = sessionmaker(bind=engine)
  return Session()

