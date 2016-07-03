# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 17:51:19
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-03 14:59:54

from tabulate import tabulate

class Constants(object):
  __floatfmt__  = '.6f'
  __tablefmt__  = 'fancy_grid'


class Formatter(object):
  """
  Format objects for output.
  """
 
  def print_list(self, items, headers, floatfmt=Constants.__floatfmt__, tablefmt=Constants.__tablefmt__):
    items = [item.tabulate() for item in items]
    self.print_result(items, headers, floatfmt=floatfmt, tablefmt=tablefmt)
  
  def print_result(self, items, headers, floatfmt=Constants.__floatfmt__, tablefmt=Constants.__tablefmt__):
    print(tabulate(items, headers, tablefmt='fancy_grid', floatfmt=floatfmt, tablefmt=tablefmt))