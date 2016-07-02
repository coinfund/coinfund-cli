# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:27:36
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-02 15:15:56

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Numeric
from sqlalchemy.orm import relationship

# Base
Base = declarative_base()

class Investor(Base):
  """
  The investor model.
  """
  __tablename__ = 'investors'
  __headers__ = ['first_name', 'last_name', 'email', 'updated_at', 'created_at']

  id          = Column(Integer, primary_key=True)
  first_name  = Column(String)
  last_name   = Column(String)
  email       = Column(String)
  updated_at  = Column(DateTime)
  created_at  = Column(DateTime)

  def tabulate(self):
    return [self.first_name, self.last_name, self.email, self.updated_at, self.created_at]

class Vehicle(Base):
  """
  The vehicle model.
  """
  __tablename__ = 'vehicles'
  __headers__   = ['name', 'description', 'url', 'currency']

  id          = Column(Integer, primary_key=True)
  name        = Column(String)
  description = Column(String)
  url         = Column(String)
  currency    = Column(String)

  def tabulate(self):
    return [self.name, self.description, self.url, self.currency]

class Position(Base):
  """
  The position model.
  """
  __tablename__ = 'positions'
  __headers__   = ['date', 'vehicle', 'position', 'currency']

  id            = Column(Integer, primary_key=True)
  date          = Column(DateTime)
  vehicle_id    = Column(Integer, ForeignKey('vehicles.id'))
  vehicle       = relationship('Vehicle')
  position      = Column(Numeric)

  def tabulate(self):
    return [self.date, self.vehicle.name, self.position, self.vehicle.currency]