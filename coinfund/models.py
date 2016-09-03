# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:27:36
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-09-03 12:25:04

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Numeric, func
from sqlalchemy.orm import relationship, validates
from datetime import datetime

# Base
Base = declarative_base()

#
# Validations
#

def validate_exists(key, value):
  assert value
  return value

class Investor(Base):
  """
  The investor model.
  """
  __tablename__   = 'investors'
  __headers__     = ['id', 'first_name', 'last_name', 'email', 'updated_at', 'created_at']

  id              = Column(Integer, primary_key=True)
  first_name      = Column(String, nullable=False)
  last_name       = Column(String, nullable=False)
  email           = Column(String, nullable=False, unique=True)
  password_digest = Column(String)
  access_token    = Column(String)
  created_at      = Column(DateTime, server_default=func.now())
  updated_at      = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

  def fullname(self):
    return ' '.join([str(item) for item in [self.first_name, self.last_name]])

  def tabulate(self):
    return [self.id, self.first_name, self.last_name, self.email, self.updated_at, self.created_at]

  @validates('first_name', 'last_name', 'email')
  def validate_exists(self, key, value):
    return validate_exists(key, value)

  def __repr__(self):
    return self.fullname()

class Instrument(Base):
  """
  The instrument model.
  """
  __tablename__   = 'instruments'
  __headers__     = ['id', 'name', 'symbol', 'created_at', 'updated_at']

  id              = Column(Integer, primary_key=True)
  name            = Column(String, nullable=False)
  symbol          = Column(String, nullable=False, unique=True)
  created_at      = Column(DateTime, server_default=func.now())
  updated_at      = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

  def tabulate(self):
    return [self.id, self.name, self.symbol, self.created_at, self.updated_at]

  @validates('name', 'symbol')
  def validate_exists(self, key, value):
    return validate_exists(key, value)

class Share(Base):
  """
  The share model.
  """
  __tablename__   = 'shares'
  __headers__     = ['id', 'investor', 'units', 'issued_date', 'created_at', 'updated_at']

  id              = Column(Integer, primary_key=True)
  investor_id     = Column(Integer, ForeignKey('investors.id'), nullable=False)
  investor        = relationship('Investor')
  units           = Column(Integer, nullable=False, default=0)
  issued_date     = Column(DateTime, server_default=func.now())
  created_at      = Column(DateTime, server_default=func.now())
  updated_at      = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

  def tabulate(self):
    return [self.id, self.investor.fullname(), self.units, self.issued_date, self.created_at, self.updated_at]  

class Project(Base):
  """
  The project model.
  """
  __tablename__   = 'projects'
  __headers__     = ['name', 'homepage', 'description', 'created_at', 'updated_at']

  id              = Column(Integer, primary_key=True)
  name            = Column(String, nullable=False)
  homepage        = Column(String)
  description     = Column(String)
  created_at      = Column(DateTime, server_default=func.now())
  updated_at      = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

  def tabulate(self):
    return [self.name, self.homepage, self.description, self.created_at, self.updated_at]


class Vehicle(Base):
  """
  The vehicle model.
  """
  __tablename__ = 'vehicles'
  __headers__   = ['name', 'instrument', 'homepage', 'description']

  id              = Column(Integer, primary_key=True)
  name            = Column(String, nullable=False)
  instr_id        = Column(Integer, ForeignKey('instruments.id'), nullable=False)
  instrument      = relationship('Instrument')
  project_id      = Column(Integer, ForeignKey('projects.id'))
  project         = relationship('Project')
  created_at      = Column(DateTime, server_default=func.now())
  updated_at      = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

  def tabulate(self):
    return [self.name, self.instrument.symbol, self.project.homepage, self.project.description]


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

class Investment(Base):
  """
  The investment model.
  """
  __tablename__   = 'investments'
  __headers__     = ['date', 'investor', 'kind', 'cost_basis_btc', 'cost_basis_usd']

  id              = Column(Integer, primary_key=True)
  date            = Column(DateTime)
  investor_id     = Column(Integer, ForeignKey('investors.id'))
  investor        = relationship('Investor')
  kind            = Column(String)
  cost_basis_btc  = Column(Numeric)
  cost_basis_usd  = Column(Numeric)

  def tabulate(self):
    return [self.date, self.investor.fullname(), self.kind, self.cost_basis_btc, self.cost_basis_usd]

class Rate(Base):
  """
  The rate model.
  """
  __tablename__   = 'convs'
  __headers__     = ['date', 'base_curr', 'to_curr', 'rate', 'source']

  id              = Column(Integer, primary_key=True)
  date            = Column(DateTime)
  base_curr       = Column(String)
  to_curr         = Column(String)
  rate            = Column(Numeric)
  source          = Column(String)

  def tabulate(self):
    return [self.date, self.base_curr, self.to_curr, self.rate]