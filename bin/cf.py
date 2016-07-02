#!/usr/bin/python

# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:44:55
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-02 15:07:01

"""CoinFund Command-Line Interface

Usage:
  cf investors
  cf vehicles
  cf positions

Options:
  -h --help     Show this screen.

"""

from docopt import docopt
from coinfund.dao import *
from coinfund.formatter import Formatter

import yaml
import sys


SETTINGS_FILE         = '.coinfund'       # name of the settings file
SETTINGS              = {}                # coinfund-cli global configuration settings
REQUIRED_SETTINGS     = ['database_uri']  # required settings

def import_settings():
  """
  Imports settings from a local file called `.coinfund`. The file is 
  in YAML format and accepts the following settings:

    database_uri: [database uri]    
  """
  global SETTINGS

  # try the settings file
  try:
    fp = open(SETTINGS_FILE, 'r')
  except:
    print('Please create a `%s` settings file.' % SETTINGS_FILE)
    fp.close()
    sys.exit(1)

  # load the settings file
  doc = yaml.load(fp)
  if not doc:
    print('Your `%s` settings file appears to be empty.' % SETTINGS_FILE)
    fp.close()
    sys.exit(1)

  # check required settings
  for setting in REQUIRED_SETTINGS:
    if setting not in doc:
      print('Please provide a `%s` setting.' % setting)
      fp.close()
      sys.exit(1)
      
  # get the settings
  SETTINGS = doc
  fp.close()

def main(args):
  """
  This function translates command arguments into
  underlying function paths.
  """

  dao = CoinfundDao(SETTINGS)   # The data access layer object.
  fmt = Formatter()             # The output formatter.

  if args['investors']:
    items = dao.investors()
    fmt.print_list(items, Investor.__headers__)

  elif args['vehicles']:
    items = dao.vehicles()
    fmt.print_list(items, Vehicle.__headers__)

  elif args['positions']:
    items = dao.positions()
    fmt.print_list(items, Position.__headers__)

  dao.close()

if __name__ == '__main__':

  # make sure cli settings are available
  import_settings()

  # parse arguments
  args = docopt(__doc__, version='coinfund-cli 1.0')
  main(args)


