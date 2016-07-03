# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:18:53
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-03 12:30:42

from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker, joinedload
from coinfund.models import Investor, Vehicle, Position, Investment, Share
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

  def vehicles(self):
    """
    Return a list of all Vehicles.
    """
    return self.session.query(Vehicle)

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

  def total_shares(self, investor_id=None):
    """
    Return total shares.
    """
    result = self.session.query(func.sum(Share.shares_issued))

    if investor_id:
      result = result.filter(Share.investor_id == investor_id)
    
    return result

  def close(self):
    """
    Close all sessions.
    """
    self.session.close_all()