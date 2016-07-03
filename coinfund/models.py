# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:27:36
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-03 16:29:58

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

# Base
Base = declarative_base()

class Investor(Base):
  """
  The investor model.
  """
  __tablename__ = 'investors'
  __headers__ = ['id', 'first_name', 'last_name', 'email', 'updated_at', 'created_at']

  id              = Column(Integer, primary_key=True)
  first_name      = Column(String, nullable=False)
  last_name       = Column(String, nullable=False)
  email           = Column(String, nullable=False, unique=True)
  password_digest = Column(String)
  access_token    = Column(String)
  updated_at      = Column(DateTime, default=datetime.now)
  created_at      = Column(DateTime, default=datetime.now, onupdate=datetime.now)

  def fullname(self):
    return ' '.join([self.first_name, self.last_name])

  def tabulate(self):
    return [self.id, self.first_name, self.last_name, self.email, self.updated_at, self.created_at]

class Instrument(Base):
  """
  The instrument model.
  """
  __tablename__   = 'instruments'
  __headers__     = ['id', 'name', 'symbol']

  id              = Column(Integer, primary_key=True)
  name            = Column(String, nullable=False)
  symbol          = Column(String, nullable=False, unique=True)

  def tabulate(self):
    return [self.id, self.name, self.symbol]

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

class Investment(Base):
  """
  The investment model.
  """
  __tablename__ = 'investments'
  __headers__   = ['date', 'investor', 'kind', 'cost_basis_btc', 'cost_basis_usd']

  id              = Column(Integer, primary_key=True)
  date            = Column(DateTime)
  investor_id     = Column(Integer, ForeignKey('investors.id'))
  investor        = relationship('Investor')
  kind            = Column(String)
  cost_basis_btc  = Column(Numeric)
  cost_basis_usd  = Column(Numeric)

  def tabulate(self):
    return [self.date, self.investor.fullname(), self.kind, self.cost_basis_btc, self.cost_basis_usd]

class Share(Base):
  """
  The share model.
  """
  __tablename__ = 'shares'
  __headers__   = ['date', 'investor', 'shares_issued', 'pps', 'cost_basis_btc', 'cost_basis_usd', 'created_at', 'updated_at']

  id              = Column(Integer, primary_key=True)
  date            = Column(DateTime)
  investor_id     = Column(Integer, ForeignKey('investors.id'))
  investor        = relationship('Investor')
  price_per_share = Column(Numeric)
  cost_basis_btc  = Column(Numeric)
  cost_basis_usd  = Column(Numeric)
  shares_issued   = Column(Integer)
  created_at      = Column(DateTime)
  updated_at      = Column(DateTime)

  def tabulate(self):
    return [self.date, self.investor.fullname(), self.shares_issued, self.price_per_share, self.cost_basis_btc, self.cost_basis_usd, self.created_at, self.updated_at]  

class Rate(Base):
  """
  The rate model.
  """
  __tablename__   = 'convs'
  __headers__     = ['date', 'base_curr', 'to_curr', 'rate']

  id              = Column(Integer, primary_key=True)
  date            = Column(DateTime)
  base_curr       = Column(String)
  to_curr         = Column(String)
  rate            = Column(Numeric)

  def tabulate(self):
    return [self.date, self.base_curr, self.to_curr, self.rate]