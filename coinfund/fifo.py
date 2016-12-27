# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-12-26 13:11:39
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-12-26 20:23:01

import pandas as pd

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
                    ]

  def __init__(self, ledgerquery):
    self.ledgerquery = ledgerquery
    self.inventory = {}
    self.taxables = self.__blanktaxables()
    pd.set_option('display.max_columns', 500)

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
    row_id    = row.id

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
                      ])

    else:
      inv               = self.inventory.get(instr)  
      unit_px           = row.usd_value / row.qty_in
      inv.loc[len(inv)] = [date, instr, qty, qty, usd_value, unit_px, row_id]

  def __processoutflow(self, row):
    date        = row.date
    instr       = row.instr_out.symbol
    total_qty   = row.qty_out
    unit_px     = row.usd_value / row.qty_out
    qty         = total_qty
    row_id      = row.id
    kind        = row.kind

    if instr in self.__FIAT:
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
                      ])
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
                       ])
        qty = 0

      else:

        invrow    = inv.iloc[0]
        queue_qty = invrow.qty
        delta     = queue_qty - qty
        acq_date  = invrow.date
        term      = self.__term(acq_date, date)

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
    
    if instr_in:
      # this is an inflow
      symbol = instr_in.symbol
      if not symbol:
        raise Exception('missing symbol on row id %s' % row.id)
      self.__ensureinstr(symbol)

      # append inflow
      self.__processinflow(row)

    if instr_out:
      symbol = instr_out.symbol
      if not symbol:
        raise Exception('missing symbol on row id %s' % row.id)
      self.__processoutflow(row)

















