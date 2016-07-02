# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 17:51:19
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-02 15:14:08

from tabulate import tabulate

class Formatter(object):
  """
  Format objects for output.
  """

  def print_list(self, items, headers):
    items = [item.tabulate() for item in items]
    print(tabulate(items, headers, tablefmt='fancy_grid', floatfmt=".6f"))
