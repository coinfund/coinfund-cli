# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-09-05 14:08:45
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-09-05 16:52:08

import csv
from coinfund.models import Ledger

class Importer(object):

  def __init__(self, dao):
    self.dao = dao

  def import_ledger(self, ledger_file):
    with open(ledger_file) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        print(row)
        entry = self.__to_entry(row)
        self.dao.create_ledger_entry(entry)
  
  def __to_entry(self, row):
      date          = row['date']
      kind          = row['kind']
      subkind       = row['subkind']
      usd_value     = row['usd_value']
      qty_in        = (row['qty_in'] or None)
      instr_in      = (row['instr_in'] or None)
      qty_out       = (row['qty_out'] or None)
      instr_out     = (row['instr_out'] or None)
      contributor   = (row['contributor'] or None)
      venue         = row['venue']
      vendor        = row['vendor']
      tx_info       = row['tx_info']
      notes         = row['notes']
      vehicle       = (row['vehicle'] or None)
      settled       = row.get('settled')

      if instr_in:
        instr_in = self.dao.instrument_by_symbol(instr_in)
      
      if instr_out:
        instr_out = self.dao.instrument_by_symbol(instr_out)

      if contributor:
        contributor = self.dao.investor_by_name(contributor)

      if vehicle:
        vehicle = self.dao.vehicle_by_name(vehicle)

      entry = Ledger( \
                date=date,
                kind=kind,
                subkind=subkind,
                usd_value=usd_value,
                qty_in=qty_in,
                instr_in=instr_in,
                qty_out=qty_out,
                instr_out=instr_out,
                contributor=contributor,
                venue=venue,
                vendor=vendor,
                tx_info=tx_info,
                notes=notes,
                vehicle=vehicle,
                settled=True   # TODO
              )
      return entry

