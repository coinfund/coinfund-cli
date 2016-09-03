# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:18:53
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-06 19:30:14

from sqlalchemy import create_engine, desc, asc, or_
from sqlalchemy.orm import sessionmaker, joinedload
from coinfund.models import Investor, Instrument, Share, Project, Vehicle, Position, Investment, Rate
from sqlalchemy.sql import func

class CoinfundDao(object):

  def __init__(self, settings):
    debug = settings.get('debug')
    self.settings = settings
    self.engine = create_engine(self.settings['database_uri'], echo=debug)
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()

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
    investor = self.session.query(Investor).filter(Investor.id == investor_id).one()
    if investor:
      self.session.delete(investor)

  def search_investor(self, query):
    query = query + '%'
    matches = self.session.query(Investor).filter( \
      or_( \
        Investor.first_name.ilike(query), \
        Investor.last_name.ilike(query), \
        Investor.email.ilike(query) \
      ) \
    )
    return matches

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
    instrument = self.session.query(Instrument).filter(Instrument.id == instrument_id).one()
    if instrument:
      self.session.delete(instrument)
    else:
      print('Could not find an instrument with id `%s`' % instrument)

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

  ### OLD

  def positions(self):
    """
    Return a list of all Positions.
    """
    result = self.session.query(Position) \
                  .options(joinedload('vehicle')) \
                  .distinct('vehicle_id') \
                  .order_by(desc('vehicle_id'), desc('date'))
    return result

  def investments(self):
    """
    Return a list of all Investments.
    """
    result = self.session.query(Investment) \
                 .options(joinedload('investor')) \
                 .order_by(asc('date'))
    return result

  def total_shares(self, investor_id=None):
    """
    Return total shares.
    """
    result = self.session.query(func.sum(Share.units))

    if investor_id:
      result =  result.filter(Share.investor_id == investor_id)
    return result

  def rates(self, instr=None):
    """
    Return latest rates.
    """
    result = self.session.query(Rate).distinct('base_curr', 'to_curr').order_by(desc('base_curr'), desc('to_curr'), desc('date'))
    if instr:
      result = result.filter(Rate.base_curr == instr)
    return result

  def commit(self):
    self.session.commit()

  def close(self):
    """
    Close all sessions.
    """
    self.session.close_all()