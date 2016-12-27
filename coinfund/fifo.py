# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-12-26 13:11:39
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-12-27 12:52:03

import pandas as pd
import pickle

class FifoProcessor():

  __KIND = {
    'Contribution': True,
    'Gift':         True,
    'Trade':        True,
    'Expense':      True,
    'Interest':     True,
    'Income':       True,
  }

  __FIAT = {
    'USD': True
  }

  __INVENTORYCOLS = [
                      'date', 
                      'instr', 
                      'qty', 
                      'original_qty', 
                      'usd_value', 
                      'unit_px', 
                      'row_id',
                    ]
  __TAXABLESCOLS  = [
                      'date', 
                      'instr', 
                      'kind', 
                      'filled_qty', 
                      'total_qty', 
                      'usd_value', 
                      'acq_date', 
                      'unit_basis_px', 
                      'unit_px', 
                      'pnl', 
                      'term', 
                      'row_id',
                      'pair_row_id',
                    ]

  __INVFILE = '.inventory'

  def __init__(self, ledgerquery, cachedinventory=False):
    """
    Take a ledger query and optional cachedinventory in
    order to perform FIFO analysis.
    """
    self.ledgerquery = ledgerquery

    if cachedinventory:
      self.inventory = self.__unpickleinventory()
      print('CACHED INVENTORY')
      for symbol, inventory in self.inventory.items():
        print('%s\n\n' % symbol)
        print('%s\n\n' % inventory.to_string())
    else:
      self.inventory = {}

    self.taxables = self.__blanktaxables()

  def __unpickleinventory(self):
    with open(self.__INVFILE, 'rb') as fp:
      return pickle.load(fp)

  def __pickleinventory(self):
    with open(self.__INVFILE, 'wb') as fp:
      pickle.dump(self.inventory, fp, protocol=pickle.HIGHEST_PROTOCOL)

  def fifo(self):
    """
    Perform FIFO analysis on the ledgerquery.
    """
    for row in self.ledgerquery:
      self.__processrow(row)
   
    for symbol, inventory in self.inventory.items():
      print('%s\n\n' % symbol)
      print('%s\n\n' % inventory.to_string())

    print(self.taxables.to_string())

  def tocsv(self):
    self.taxables.to_csv('taxables.csv')

  def inventorycsv(self):
    df = pd.concat([df for df in self.inventory.values()])
    df.to_csv('inventory.csv')

  def cacheinventory(self):
    self.__pickleinventory()

  def __blankinventory(self):
    """Return a blank dataframe for inventories."""
    return pd.DataFrame([], columns=self.__INVENTORYCOLS)

  def __blanktaxables(self):
    """Return a blank datafrome for taxables."""
    return pd.DataFrame([], columns=self.__TAXABLESCOLS)

  def __ensureinstr(self, symbol):
    """
    Ensure a data frame for a symbol, except fiat.
    """
    if not symbol in self.inventory and not symbol in self.__FIAT:
      self.inventory[symbol] = self.__blankinventory()

  def __taxable(self, row):
    l = len(self.taxables)
    self.taxables.loc[l] = row

  def __term(self, acq_date, tx_date):
    if tx_date < acq_date:
      raise Exception('tx date must come after acq date')

    delta = tx_date - acq_date
    if delta.days >= 365:
      return 'Long-Term'
    else:
      return 'Short-Term'

  def __processinflow(self, row):
    date      = row.date
    instr     = row.instr_in.symbol
    kind      = row.kind
    qty       = row.qty_in
    usd_value = row.usd_value
    row_id    = int(row.id)

    # skip USD inflows, unless they are income
    # or interest
    if row.instr_in.symbol in self.__FIAT:
      if row.kind in ['Income', 'Interest', 'Gift']:
        self.__taxable([
                        date, 
                        instr, 
                        kind, 
                        None, 
                        qty, 
                        usd_value, 
                        None, 
                        0.0, 
                        None, 
                        usd_value, 
                        None, 
                        row_id,
                        None,
                      ])

    else:
      inv               = self.inventory[instr]  
      unit_px           = row.usd_value / row.qty_in
      new_row           = pd.DataFrame([[date, instr, qty, qty, usd_value, unit_px, row_id]], columns=self.__INVENTORYCOLS)

      self.inventory[instr] = inv.append(new_row, ignore_index=True)
      
  def __processoutflow(self, row):
    date        = row.date
    instr       = row.instr_out.symbol
    total_qty   = row.qty_out
    unit_px     = row.usd_value / row.qty_out
    qty         = total_qty
    row_id      = int(row.id)
    kind        = row.kind

    if row.kind in ['Expense']:
      pnl = -1 * row.usd_value
      self.__taxable([
                      date, 
                      instr, 
                      kind, 
                      None, 
                      qty, 
                      row.usd_value,
                      None, 
                      None, 
                      None, 
                      pnl, 
                      None, 
                      row_id,
                      None,
                    ])
      # If the expense is paid in fiat,
      # there is nothing else to do except
      # record loss.
      if instr in self.__FIAT:
        return



    inv = self.inventory.get(instr)  
    while qty > 0:
  
      # if we run out of inventory
      if (inv is None) or (len(inv) == 0):

        filled_qty            = qty
        usd_value             = row.usd_value
        pnl                   = row.usd_value
        unit_basis_px         = 0.0
        term                  = 'Short-Term'
        acq_date              = None
        
        self.__taxable([
                        date, 
                        instr, 
                        kind, 
                        filled_qty, 
                        total_qty, 
                        usd_value, 
                        acq_date, 
                        unit_basis_px, 
                        unit_px, 
                        pnl, 
                        term, 
                        row_id,
                        None,
                       ])
        qty = 0

      else:

        invrow      = inv.iloc[0]
        queue_qty   = invrow.qty
        delta       = queue_qty - qty
        acq_date    = invrow.date
        term        = self.__term(acq_date, date)
        pair_row_id = int(invrow.row_id)

        if delta >= 0:

          inv.ix[inv.index[0], 'qty'] = delta
          
          filled_qty      = qty
          usd_value       = row.usd_value
          unit_basis_px   = invrow.unit_px
          pnl             = (unit_px - unit_basis_px) * filled_qty

          self.__taxable([
                          date, 
                          instr, 
                          kind, 
                          filled_qty, 
                          total_qty, 
                          usd_value, 
                          acq_date, 
                          unit_basis_px, 
                          unit_px, 
                          pnl, 
                          term, 
                          row_id,
                          pair_row_id,
                        ])

          # if we have exhausted the queue item,
          # drop it
          if delta == 0:
            inv.drop(inv.index[[0]], inplace=True)
          qty = 0

        else:

          filled_qty     = queue_qty
          usd_value      = queue_qty * unit_px
          unit_basis_px  = invrow.unit_px
          pnl            = (unit_px - unit_basis_px) * filled_qty

          self.__taxable([
                          date, 
                          instr, 
                          kind, 
                          filled_qty, 
                          total_qty, 
                          usd_value, 
                          acq_date, 
                          unit_basis_px, 
                          unit_px, 
                          pnl, 
                          term, 
                          row_id,
                          pair_row_id,
                        ])

          # drop the inventory
          inv.drop(inv.index[[0]], inplace=True)
          qty -= filled_qty



  def __processrow(self, row):
    """
    Process a ledger row.
    """

    # check whether this is an inflow or outflow
    instr_in  = row.instr_in
    instr_out = row.instr_out
    
    print('=> %s in %s/%s out %s/%s\n' % (row.kind, row.instr_in, row.qty_in, row.instr_out, row.qty_out))

    if instr_in:
      # this is an inflow
      symbol = instr_in.symbol
      if not symbol:
        raise Exception('missing symbol on row id %s' % row.id)
      self.__ensureinstr(symbol)

      # append inflow
      self.__processinflow(row)
      if symbol not in self.__FIAT:
        print('-------------------------------\n%s\n' % self.inventory[symbol].to_string())

    if instr_out:
      symbol = instr_out.symbol
      if not symbol:
        raise Exception('missing symbol on row id %s' % row.id)
      self.__processoutflow(row)
      if symbol not in self.__FIAT:
        print('-------------------------------\n%s\n' % self.inventory[symbol].to_string())


    
















