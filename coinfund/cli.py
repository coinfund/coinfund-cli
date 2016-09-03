# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-03 11:01:22
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-09-03 12:57:43

from coinfund.models import *
from coinfund.formatter import Formatter
import datetime

class Dispatcher(object):

  def __init__(self, dao):
    self.dao = dao
    self.fmt = Formatter()
    self.cli = Cli(self.dao, self.fmt)

  def dispatch(self, args):
    
    #
    # Investors
    #
    if args['investors']:

      #
      # Add an investor
      #
      if args['add']:
        investor = self.cli.new_investor()
        self.dao.create_investor(investor)

      elif args['delete']:
        investor_id = args.get('--investor-id')
        if investor_id:
          self.dao.delete_investor(investor_id)
        else:
          print('Could not find investor id `%s`' % investor_id)
      #
      # List all investors
      #
      else:
        items = self.dao.investors()
        self.fmt.print_list(items, Investor.__headers__)

    #
    # Instruments
    #
    elif args['instruments']:

      if args['add']:
        instrument = self.cli.new_instrument()
        self.dao.create_instrument(instrument)

      elif args['delete']:
        instrument_id = args.get('--instrument-id')
        if instrument_id:
          self.dao.delete_instrument(instrument_id)
        else:
          print('Could not find instrument id `%s`' % instrument_id)
      
      else:
        items = self.dao.instruments()
        self.fmt.print_list(items, Instrument.__headers__)

    #
    # Shares
    #
    elif args['shares']:

      if args['add']:
        share = self.cli.new_share()
        self.dao.create_share(share)

      elif args['delete']:
        share_id = args.get('--share-id')
        if share_id:
          self.dao.delete_share(share_id)
        else:
          print('Could not find share id `%s`' % share_id)

      else:
        total = args.get('--total')
        investor_id = None
        
        if total:
          if args.get('--investor'):
            investor = self.cli.search_investor()
            if investor:
              investor_id = investor.id          
          items = self.dao.total_shares(investor_id=investor_id)
          self.fmt.print_result(items, ['total_shares'])
        else:   
          items = self.dao.shares(investor_id=investor_id)
          self.fmt.print_list(items, Share.__headers__)

    elif args['projects']:
      items = self.dao.projects()
      self.fmt.print_list(items, Project.__headers__)

    elif args['investments']:
      items = self.dao.investments()
      self.fmt.print_list(items, Investment.__headers__)

    elif args['vehicles']:
      items = self.dao.vehicles()
      self.fmt.print_list(items, Vehicle.__headers__)

    elif args['positions']:
      items = self.dao.positions()
      self.fmt.print_list(items, Position.__headers__)

    elif args['rates']:
      instr = args.get('--instr')
      items = self.dao.rates(instr=instr)
      self.fmt.print_list(items, Rate.__headers__, floatfmt='.8f')

    self.dao.commit()
    self.dao.close()

class Cli(object):

  """
  Cli implements a command line interface for taking
  command line input for business objects.
  """

  def __init__(self, dao, fmt):
    """
    """
    self.dao = dao
    self.fmt = fmt

  def new_investor(self):
    first_name = input('First name: ')
    last_name  = input('Last name: ')
    email      = input('Email: ')
    investor = Investor(first_name=first_name, last_name=last_name, email=email)
    return investor

  def new_instrument(self):
    name       = input('Name: ')
    symbol     = input('Symbol: ')
    instrument = Instrument(name=name, symbol=symbol)
    return instrument

  def search_investor(self):
    investor_query = input('Investor search: ')
    matches        = self.dao.search_investor(investor_query).all()

    if not matches:
      print('Could not find investor matching `%s`. Try again.' % investor_query)

    elif len(matches) == 1:
      investor = matches[0]
      print('-> %s' % investor)
      return investor

    elif len(matches) > 1:
      self.fmt.print_list(matches, Investor.__headers__)
      investor_id = input('Investor id: ')
      investor = None
      for match in matches:
        if match.id == investor_id:
          return match
    
  def new_share(self):
    investor = self.search_investor()

    if not investor:
      raise Exception('Could not find investor record.')
    
    units = input('Units: ')
    issued_date = input('Date issued [YYYY-MM-DD]: ')
    
    share = Share(investor_id=investor.id, units=units, issued_date=(issued_date or None))
    return share
      
