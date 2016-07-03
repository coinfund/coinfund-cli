# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:18:53
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-03 17:32:11

from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker, joinedload
from coinfund.models import Investor, Instrument, Share, Project, Vehicle, Position, Investment, Rate
from sqlalchemy.sql import func

class CoinfundDao(object):

  def __init__(self, settings):
    self.settings = settings

    debug = self.settings.get('debug')

    self.engine = create_engine(self.settings['database_uri'], echo=debug)
    self.Session = sessionmaker(bind=self.engine)
    self.session = self.Session()

  def settings(self):
    """
    Return the settings for this DAO.
    """
    return self.settings

  def investors(self):
    """
    Return a list of all Investors.
    """
    return self.session.query(Investor)

  def instruments(self):
    """
    Return a list of all Instruments.
    """
    return self.session.query(Instrument).order_by(asc('symbol'))

  def vehicles(self):
    """
    Return a list of all Vehicles.
    """
    return self.session.query(Vehicle)

  def shares(self, investor_id=None):
    """
    Return a list of all Shares.
    """
    result = self.session.query(Share) \
                 .options(joinedload('investor')) \
                 .order_by(asc('date'))

    if investor_id:
      result = result.filter(Share.investor_id == investor_id)

    return result

  def projects(self):
    """
    Return a list of all Projects.
    """
    result = self.session.query(Project)
    return result

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

  def close(self):
    """
    Close all sessions.
    """
    self.session.close_all()