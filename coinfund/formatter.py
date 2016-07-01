# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 17:51:19
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-01 17:57:58

from tabulate import tabulate

class Formatter(object):
  """
  Format objects for output.
  """

  def print_list(self, items, model):
    items = [item.tabulate() for item in items]
    print(tabulate(items, model.__headers__, tablefmt='fancy_grid'))