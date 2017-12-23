# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-03 11:01:22
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-12-26 20:59:30

from coinfund.models import *
from coinfund.formatter import Formatter
from coinfund.importer import Importer
from coinfund.fifo import FifoProcessor
import datetime
import inflection

class Dispatcher(object):

  headers = {
    'investors': Investor.__headers__,
    'instruments': Instrument.__headers__,
    'vehicles': Vehicle.__headers__,
  }

  def __init__(self, dao):
    self.dao = dao
    self.fmt = Formatter()
    self.cli = Cli(self.dao, self.fmt)

  def __resources(self, resource):
    """
    Print the vanilla listing for a resource.
    """
    resource = inflection.pluralize(resource)
    items = getattr(self.dao, resource)()
    self.fmt.print_list(items, self.headers[resource])

  def __add_resource(self, resource):
    """
    Add a vanilla resource.
    """
    resource  = inflection.singularize(resource)
    item      = getattr(self.cli, 'new_' + resource)()
    create    = getattr(self.dao, 'create_' + resource)
    create(item)

  def __delete_resource(self, resource, resource_id=None):
    """
    Delete a vanilla resource.
    """
    resource = inflection.singularize(resource)
    if not resource_id:
      item = getattr(self.cli, 'search_' + resource)()
      resource_id = item.id
    delete = getattr(self.dao, 'delete_' + resource)
    delete(resource_id)

  def __search_resource(self, resource):
    resource = inflection.singularize(resource)
    search_fn = getattr(self.cli, 'search_' + resource)
    search_fn()

  def __basic_resource_functions(self, args, resource):
    resource_id = args.get('--id')
    if args['add']:
      self.__add_resource(resource)
    elif args['delete']:
      self.__delete_resource(resource, resource_id)
    elif args['search']:
      self.__search_resource(resource)  
    else:
      self.__resources(resource)   

  def dispatch(self, args):
    
    #
    # Investors
    #
    if args['investors']:
      self.__basic_resource_functions(args, 'investor')

    #
    # Instruments
    #
    elif args['instruments']:
      self.__basic_resource_functions(args, 'instrument')

    #
    # Vehicles
    #
    elif args['vehicles']:
      self.__basic_resource_functions(args, 'vehicle')

    #
    # Projects
    #
    elif args['projects']:
      self.__basic_resource_functions(args, 'project')

    #
    # Shares
    #
    elif args['shares']:
      resource = 'share'
      resource_id = args.get('--id')

      if args['add']:
        self.__add_resource(resource)

      elif args['delete']:
        self.__delete_resource(resource, resource_id)

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

      kind            = args.get('--kind')
      startdate       = args.get('--startdate')
      enddate         = args.get('--enddate')
      total           = args.get('--total')
      instr           = args.get('--instr')
      date            = args.get('--date')
      sale            = args.get('--sale')
      entry_id        = args.get('--id')
      tocsv           = args.get('--tocsv')
      invcsv          = args.get('--inventorycsv')
      cache           = args.get('--cache')
      usecache        = args.get('--usecache')
      useinventorycsv = args.get('--userinventorycsv')

      if args['add']:
        ledger_entry = self.cli.new_ledger_entry()
        self.dao.create_ledger_entry(ledger_entry)

        # print
        items = self.dao.ledger()
        self.fmt.print_list(items, Ledger.__headers__)

      elif args['delete']:
        self.dao.delete_ledger_entry(entry_id)
        
      elif args['contributions']:
        if total:
          items = self.dao.total_ledger(kind='Contribution', startdate=startdate, enddate=enddate)
          self.fmt.print_result(items, ['total_ledger_contributions'])
        else:
          items = self.dao.ledger(kind='Contribution', startdate=startdate, enddate=enddate)
          self.fmt.print_list(items, Ledger.__headers__)

      elif args['expenses']:
        if total:
          items = self.dao.total_ledger(kind='Expense', startdate=startdate, enddate=enddate)
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

      elif args['basis']:
        items = self.dao.total_ledger(startdate=startdate, enddate=enddate, date=date, instr=instr, sale=sale)
        self.fmt.print_result(items, ['usd_value', 'qty', 'avg_usd_price'])
      
      elif args['fifo']:

        items = self.dao.ledger(kind=kind, startdate=startdate, enddate=enddate, date=date, instr=instr)
        self.fmt.print_list(items, Ledger.__headers__)
        
        fp = FifoProcessor(items)

        if usecache:
          fp.load_inventory_from_cache()
        elif useinventorycsv:
          fp.load_inventory_from_csv(userinventorycsv)

        fp.fifo()

        if tocsv:
          fp.tocsv()
        if invcsv:
          fp.inventorycsv()
        if cache:
          fp.cacheinventory()

      elif args['inventory']:
        fromcache     = args.get('--fromcache')
        fromcsv       = args.get('--fromcsv')

        fp = FifoProcessor()

        if fromcsv:
          fp.load_inventory_from_csv(fromcsv)

        else:
          fp.load_inventory_from_cache()
        
        for (key, value) in fp.inventory.items():
          print('\n', key, '\n')
          self.fmt.print_result(value, ['date', 'instr', 'qty', 'original_qty', 'usd_value', 'unit_px', 'row_id'])

      else:
        items = self.dao.ledger(kind=kind, startdate=startdate, enddate=enddate, date=date, instr=instr)
        self.fmt.print_list(items, Ledger.__headers__)


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

    elif len(matches) > 1:
      self.fmt.print_list(matches, Instrument.__headers__)
      instr_id = input('Instrument id: ')
      instr = None
      if instr_id:
        for match in matches:
          if match.id == int(instr_id):
            return match

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

    elif len(matches) > 1:
      self.fmt.print_list(matches, Vehicle.__headers__)
      vehicle_id = input('Vehicle id: ')
      vehicle = None
      if vehicle_id:
        for match in matches:
          if match.id == int(vehicle_id):
            return match

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
      if investor_id:
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

