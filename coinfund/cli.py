# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-03 11:01:22
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-09-05 17:33:16

from coinfund.models import *
from coinfund.formatter import Formatter
from coinfund.importer import Importer
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
        investor = self.cli.search_investor()

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
        investor_only = args.get('--investor')
        investor_id = None
        
        if total:
          if investor_only:
            investor = self.cli.search_investor()
            if investor:
              investor_id = investor.id          
          items = self.dao.total_shares(investor_id=investor_id)
          self.fmt.print_result(items, ['total_shares'])

        else:
          if investor_only: 
            investor = self.cli.search_investor() 
            if investor:
              investor_id = investor.id
          items = self.dao.shares(investor_id=investor_id)
          self.fmt.print_list(items, Share.__headers__)

    #
    # LEDGER
    #
    elif args['ledger']:

      kind      = args.get('--kind')
      startdate = args.get('--startdate')
      enddate   = args.get('--enddate')
      total     = args.get('--total')
      instr     = args.get('--instr')

      if args['add']:
        ledger_entry = self.cli.new_ledger_entry()
        self.dao.create_ledger_entry(ledger_entry)

        # print
        items = self.dao.ledger()
        self.fmt.print_list(items, Ledger.__headers__)

      elif args['delete']:
        entry_id = args.get('--entry-id')
        if entry_id:
          self.dao.delete_ledger_entry(entry_id)
        else:
          print('Could not find entry id `%s`.' % entry_id)

      elif args['contributions']:
        if total:
          items = self.dao.total_ledger('Contribution', startdate=startdate, enddate=enddate)
          self.fmt.print_result(items, ['total_ledger_contributions'])
        else:
          items = self.dao.ledger(kind='Contribution', startdate=startdate, enddate=enddate)
          self.fmt.print_list(items, Ledger.__headers__)

      elif args['expenses']:
        if total:
          items = self.dao.total_ledger('Expense', startdate=startdate, enddate=enddate)
          self.fmt.print_result(items, ['total_ledger_expenses'])
        else:
          items = self.dao.ledger(kind='Expense', startdate=startdate, enddate=enddate)
          self.fmt.print_list(items, Ledger.__headers__)

      elif args['import']:
        ledger_file = args.get('--file')
        if not ledger_file:
          raise Exception('Please specify --file.')

        importer = Importer(self.dao)
        importer.import_ledger(ledger_file)

      else:
        items = self.dao.ledger(kind=kind, startdate=startdate, enddate=enddate, instr=instr)
        self.fmt.print_list(items, Ledger.__headers__)

    elif args['projects']:
      items = self.dao.projects()
      self.fmt.print_list(items, Project.__headers__)

    elif args['vehicles']:
      
      if args['add']:
        vehicle = self.cli.new_vehicle()
        self.dao.create_vehicle(vehicle)

      elif args['delete']:
        vehicle_id = args.get('--vehicle-id')
        if not vehicle_id:
          raise Exception('Provide a valid id.')

        try:
          self.dao.delete_vehicle(vehicle_id)
        except:
          raise Exception('Could not find vehicle with id `%s`' % vehicle_id)

      else:
        items = self.dao.vehicles()
        self.fmt.print_list(items, Vehicle.__headers__)

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

  def new_vehicle(self):
    """
    Create a new vehicle.
    """
    name      = input('Name: ')
    instr     = self.search_instrument()

    vehicle   = Vehicle(name=name, instr_id=instr.id)
    return vehicle


  def new_ledger_entry(self):
    date          = input('Date [YYYY-MM-DD]: ') or None
    kind          = input('Kind: ')
    subkind       = None
    qty_in        = None
    instr_in      = None
    qty_out       = None
    instr_out     = None
    contributor   = None
    venue         = None
    vendor        = None
    tx_info       = None
    notes         = None
    settled       = True
    vehicle       = self.search_vehicle()
    
    if date:
      date = datetime.datetime.strptime(date, "%Y-%m-%d")    

    if kind == 'Expense':
      subkind       = input('Subkind: ') or None
  
    usd_value     = input('USD Value: ')

    if kind not in ('Expense'):
      qty_in        = input('Qty in: ') or None
      if qty_in:
        instr_in = self.search_instrument()

    if kind not in ('Contribution', 'Income', 'Reimbursement'):
      qty_out       = input('Qty out: ') or None
      if qty_out:
        instr_out = self.search_instrument()

    if kind == 'Contribution':
      contributor = self.search_investor()

    if kind == 'Expense':
      vendor   = input('Vendor: ')

    venue         = input('Venue: ')
    tx_info       = input('Tx info: ')
    notes         = input('Notes: ')
    entry = Ledger(date=(date or None), \
                   kind=kind, \
                   subkind=subkind, \
                   usd_value=usd_value, \
                   qty_in=qty_in, \
                   instr_in=instr_in, \
                   qty_out=qty_out, \
                   instr_out=instr_out, \
                   contributor=contributor, \
                   venue=venue, \
                   vendor=vendor, \
                   tx_info=tx_info, \
                   notes=notes, \
                   vehicle=vehicle, \
                   settled=settled \
            )

    return entry

  def search_instrument(self):
    """
    Interactively search for an instrument.
    """
    query      = input('Instrument search: ')
    matches    = self.dao.search_instrument(query).all()

    if len(matches) == 1:
      instr = matches[0]
      print('-> %s' % instr.symbol)
      return instr

    raise Exception('Could not find instrument record.')

  def search_vehicle(self):
    """
    Interactively search for a vehicle.
    """

    query      = input('Vehicle search: ')
    matches    = self.dao.search_vehicle(query).all()

    if len(matches) == 1:
      vehicle = matches[0]
      print('-> %s' % vehicle.name)
      return vehicle

    raise Exception('Could not find vehicle record.')

  def search_investor(self):
    """
    Interactively search for an investor.
    """
    investor_query = input('Investor search: ')
    matches        = self.dao.search_investor(investor_query).all()

    if len(matches) == 1:
      investor = matches[0]
      print('-> %s' % investor)
      return investor

    elif len(matches) > 1:
      self.fmt.print_list(matches, Investor.__headers__)
      investor_id = input('Investor id: ')
      investor = None
      for match in matches:
        if match.id == int(investor_id):
          return match

    raise Exception('Cound not find investor record.' )
    
  def new_share(self):
    investor = self.search_investor()

    units = input('Units: ')
    issued_date = input('Date issued [YYYY-MM-DD]: ')

    share = Share(investor_id=investor.id, units=units, issued_date=(issued_date or None))
    return share
      
