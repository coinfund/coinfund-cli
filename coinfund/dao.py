# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:18:53
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-09-05 17:15:03

from sqlalchemy import create_engine, desc, asc, or_
from sqlalchemy.orm import sessionmaker, joinedload
from coinfund.models import Investor, Instrument, Share, Project, Vehicle, Ledger
from sqlalchemy.sql import func

class CoinfundDao(object):

  def __init__(self, settings):
    debug = settings.get('debug')
    self.settings = settings
    self.engine = create_engine(self.settings['database_uri'], echo=debug)
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()
    self.instr_cache = {}
    self.vehicle_cache = {}

  def settings(self):
    """
    Return the settings for this DAO.
    """
    return self.settings

  def investor(self, investor_id):
    """
    Get an investor by id.
    """
    return self.session.query(Investor).get(investor_id)

  def investors(self):
    """
    Return a list of all Investors.
    """
    return self.session.query(Investor)

  def create_investor(self, investor):
    """
    Create an investor record.
    """
    self.session.add(investor)

  def delete_investor(self, investor_id):
    """
    Delete an investor record.
    """
    investor = self.session.query(Investor).filter(Investor.id == investor_id).one()
    if investor:
      self.session.delete(investor)

  def search_investor(self, query):
    """
    Search for an investor by name or email.
    """
    query = query + '%'
    matches = self.session.query(Investor).filter( \
      or_( \
        Investor.first_name.ilike(query), \
        Investor.last_name.ilike(query), \
        Investor.email.ilike(query) \
      ) \
    )
    return matches

  def investor_by_name(self, fullname):
    """
    Search for an investor by full name.
    """
    match = self.session.query(Investor).filter(
      Investor.fullname == fullname
    ).one()
    if not match:
      raise Exception('Could not find investor for `%s`' % fullname)
    return match

  def instruments(self):
    """
    Return a list of all Instruments.
    """
    return self.session.query(Instrument).order_by(asc('symbol'))

  def create_instrument(self, instrument):
    """
    Create an instrument record.
    """
    self.session.add(instrument)

  def delete_instrument(self, instrument_id):
    """
    Delete an instrument.
    """
    instrument = self.session.query(Instrument).filter(Instrument.id == instrument_id).one()
    if instrument:
      self.session.delete(instrument)
    else:
      print('Could not find an instrument with id `%s`' % instrument_id)

  def search_instrument(self, query):
    """
    Search for an instrument by name or symbol.
    """
    query = query + '%'
    matches = self.session.query(Instrument).filter( \
      or_( \
        Instrument.name.ilike(query), \
        Instrument.symbol.ilike(query) \
      ) \
    )
    return matches

  def instrument_by_symbol(self, symbol):
    if symbol in self.instr_cache:
      return self.instr_cache[symbol]
    else:
      match = self.session.query(Instrument).filter(Instrument.symbol == symbol).one()
      if match:
        self.instr_cache[symbol] = match
        return match
      else:
        raise Exception('Could not find instrument for symbol `%s`' % symbol)

  def shares(self, investor_id=None):
    """
    Return a list of all Shares.
    """
    result = self.session.query(Share) \
                 .options(joinedload('investor')) \
                 .order_by(asc('created_at'))

    if investor_id:
      result = result.filter(Share.investor_id == investor_id)

    return result

  def total_shares(self, investor_id=None):
    """
    Return total shares.
    """
    result = self.session.query(func.sum(Share.units))

    if investor_id:
      result =  result.filter(Share.investor_id == investor_id)
    return result

  def create_share(self, share):
    """
    Create a share entry.
    """
    self.session.add(share)

  def delete_share(self, share_id=None):
    share = self.session.query(Share).filter(Share.id == share_id).one()
    if share:
      self.session.delete(share)
    else:
      print('Could not find a share with id `%s`' % share_id)

  def ledger(self, kind=None, startdate=None, enddate=None):
    """
    Return ledger entries.
    """
    result = self.session.query(Ledger).order_by(Ledger.date)

    if kind:
      result = result.filter(Ledger.kind == kind)
    if startdate:
      result = result.filter(Ledger.date >= startdate)
    if enddate:
      result = result.filter(Ledger.date <= enddate)

    return result

  def create_ledger_entry(self, ledger_entry):
    """
    Create a ledger entry.
    """
    self.session.add(ledger_entry)

  def delete_ledger_entry(self, entry_id):
    """
    Delete a ledger entry.
    """
    ledger_entry = self.session.query(Ledger).filter(Ledger.id == entry_id).one()
    if ledger_entry:
      self.session.delete(ledger_entry)
    else:
      print('Could not find a ledger entry with id `%s`' % entry_id)

  def total_ledger(self, kind, startdate=None, enddate=None):
    """
    Return total ledger usd values.
    """
    result = self.session.query(func.sum(Ledger.usd_value)).filter(Ledger.kind == kind)

    if startdate:
      result = result.filter(Ledger.date >= startdate)

    if enddate:
      result = result.filter(Ledger.date <= enddate)

    return result


  def projects(self):
    """
    Return a list of all Projects.
    """
    result = self.session.query(Project)
    return result

  def vehicles(self):
    """
    Return a list of all Vehicles.
    """
    return self.session.query(Vehicle).options(joinedload('instrument'), joinedload('project'))

  def create_vehicle(self, vehicle):
    """
    Create a new vehicle.
    """
    self.session.add(vehicle)

  def delete_vehicle(self, vehicle_id):
    """
    Delete a vehicle.
    """
    vehicle = self.session.query(Vehicle).filter(Vehicle.id == vehicle_id).one()
    self.session.delete(vehicle)
  
  def search_vehicle(self, query):
    """
    Search for an vehicle by name or symbol.
    """
    query = query + '%'
    matches = self.session.query(Vehicle).join(Instrument).filter( \
      or_( \
        Vehicle.name.ilike(query), \
        Instrument.symbol.ilike(query) \
      ) \
    )
    return matches

  def vehicle_by_name(self, name):
    if name in self.vehicle_cache:
      return self.vehicle_cache[name]
    else:
      match = self.session.query(Vehicle).filter(Vehicle.name == name).one()
      if match:
        self.vehicle_cache[name] = match
        return match
      else:
        raise Exception('Could not find vehicle with name `%s`' % name)

  def commit(self):
    self.session.commit()

  def close(self):
    """
    Close all sessions.
    """
    self.session.close_all()