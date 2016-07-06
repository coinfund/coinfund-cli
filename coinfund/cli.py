# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-03 11:01:22
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-06 16:12:21

from coinfund.models import *
from coinfund.formatter import Formatter

class Dispatcher(object):

  def __init__(self, dao):
    self.dao = dao
    self.fmt = Formatter()
    self.cli = Cli()

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

    elif args['shares']:
      total = args.get('--total')
      investor_id = args.get('--investor-id')
      
      if total:
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