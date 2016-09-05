# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:27:36
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-09-05 13:52:28

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Numeric, func, Boolean
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
  issued_date     = Column(DateTime)
  created_at      = Column(DateTime)
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
    homepage = None
    description = None
    if self.project:
      homepage = self.project.homepage
      description = self.project.description
    return [self.name, self.instrument.symbol, homepage, description]


class Ledger(Base):
  """
  The ledger model.
  """
  __tablename__   = 'ledger'
  __headers__     = ['id', 'vehicle', 'date', 'kind', 'subkind', 'usd_value', 'qty_in', 'instr_in', 'qty_out', 'instr_out', 'contributor', 'venue', 'vendor', 'tx_info', 'notes']

  id              = Column(Integer, primary_key=True)
  date            = Column(DateTime, nullable=False, server_default=func.now())
  kind            = Column(String, nullable=False)
  subkind         = Column(String)
  usd_value       = Column(Numeric)
  qty_in          = Column(Numeric)
  instr_in_id     = Column(Integer, ForeignKey('instruments.id'))
  instr_in        = relationship(Instrument, foreign_keys='Ledger.instr_in_id')
  qty_out         = Column(Numeric)
  instr_out_id    = Column(Integer, ForeignKey('instruments.id'))
  instr_out       = relationship(Instrument, foreign_keys='Ledger.instr_out_id') 
  contributor_id  = Column(Integer, ForeignKey('investors.id'))
  contributor     = relationship(Investor)
  venue           = Column(String)
  vendor          = Column(String)
  tx_info         = Column(String)
  settled         = Column(Boolean)
  source          = Column(String)
  vehicle_id      = Column(Integer, ForeignKey('vehicles.id'))
  vehicle         = relationship(Vehicle)
  notes           = Column(String)

  @validates('kind')
  def validate_exists(self, key, value):
    return validate_exists(key, value)

  def tabulate(self):
    instr_in = None
    instr_out = None
    contributor = None
    vehicle = None
    if self.instr_in:
      instr_in = self.instr_in.symbol
    if self.instr_out:
      instr_out = self.instr_out.symbol
    if self.contributor:
      contributor = self.contributor.fullname()
    if self.vehicle:
      vehicle = vehicle.name

    return [self.id, vehicle, self.date.date(), self.kind, self.subkind, self.usd_value, self.qty_in, instr_in , self.qty_out, instr_out, \
      contributor, self.venue, self.vendor, self.tx_info[:25], self.notes[:30]
    ]
