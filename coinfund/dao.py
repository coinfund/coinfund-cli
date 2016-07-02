# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:18:53
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-02 15:12:11

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, joinedload
from coinfund.models import Investor, Vehicle, Position

class CoinfundDao(object):

  def __init__(self, settings):
    self.settings = settings
    self.engine = create_engine(self.settings['database_uri'], echo=True)
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
    result = self.session.query(Position).options(joinedload('vehicle')).join(Vehicle).distinct('vehicle_id').order_by(desc('vehicle_id'), desc('date'))
    print(result)
    return result

  def close(self):
    """
    Close all sessions.
    """
    self.session.close_all()