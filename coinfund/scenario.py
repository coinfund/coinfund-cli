# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2017-12-23
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-12-23 

import pandas as pd

from coinfund.prices import Price
from coinfund.formatter import Formatter

from decimal import Decimal
from datetime import datetime

class Scenario(object):

    def __init__(self, inventory, ltrate=Decimal(.38), strate=Decimal(.52)):
        self.inventory = inventory
        self.price     = Price()
        self.ltrate    = ltrate
        self.strate    = strate
        self.fmt       = Formatter()

    def __getliability(self, gains, acq_date, tx_date):
        if tx_date < acq_date:
          raise Exception('tx date must come after acq date')

        if gains <= 0:
            return Decimal(0)

        delta = tx_date - acq_date
        if delta.days >= 365:
          return self.ltrate * gains
        else:
          return self.strate * gains

    def asset_liquidation(self, instr, proceedslimit=None):

        if self.inventory[instr].empty:
            raise Exception('No such asset in inventory.')

        if proceedslimit:
            proceedslimit = Decimal(proceedslimit)

        inv   = self.inventory[instr]
        px    = self.price.of(instr)
        today = datetime.now()

        print('px: %.2f' % px)

        total_qty         = Decimal(0)
        total_proceeds    = Decimal(0)
        total_gains       = Decimal(0)
        total_liability   = Decimal(0)
        total_lossrate    = Decimal(0)
        total_netproceeds = Decimal(0)

        report_rows = []
        report_header = ['instr', 'qty', 'liq_px', 'unit_px', 'acq_date', 'proceeds', 'gains', 'liability', 'netproceeds', 'lossrate']
        terminate = False
            
        for inx, row in inv.iterrows():
        
            qty                 = Decimal(row.qty)
            proceeds            = px * qty
           
            # check for proceeds limit
            if proceedslimit:
                deltaproceeds = proceedslimit - total_proceeds
                if proceeds > deltaproceeds:
                    qty = deltaproceeds /  px
                    proceeds = px * qty
                    terminate = True

            unit_px             = Decimal(row.unit_px)
            gains               = qty * (px - unit_px)
            liability           = self.__getliability(gains, row.date, today)
            netproceeds         = proceeds - liability
            lossrate            = max(liability / proceeds,0)

            total_qty           += qty
            total_proceeds      += proceeds
            total_gains         += gains
            total_liability     += liability
            total_netproceeds   += netproceeds

            report_rows.append([instr, qty, px, unit_px, row.date, proceeds, gains, liability, netproceeds, lossrate])
          
            if terminate:
                break

        self.fmt.print_result(report_rows, report_header)
        total_lossrate = total_liability / total_proceeds
        self.fmt.print_result([[instr, total_qty, px, None, None, total_proceeds, total_gains, total_liability, total_netproceeds, total_lossrate]], report_header)