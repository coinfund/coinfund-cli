#!/usr/bin/python

# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:44:55
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-01 12:07:51

"""CoinFund Command-Line Interface

Usage:
  cf.py vehicles

Options:
  -h --help     Show this screen.

"""

from docopt import docopt

import yaml
import sys

SETTINGS = {}
def import_settings():
  """
  Imports settings from a local file called `.coinfund-cli`. The file is 
  in YAML format and accepts the following settings:

    database_uri: [database uri]    
  
  """
  try:
    with open('.coinfund-cli', 'r') as fp:
      doc = yaml.load(fp)
      if not doc['database_uri']:
        print "Please provide a `database_uri` setting."
        sys.exit(1)
      else:
        SETTINGS = doc
  except:
    print "Please create a .coinfund-cli settings file."
    sys.exit(1)


if __name__ == '__main__':

  # make sure cli settings are available
  import_settings()

  # parse arguments
  args = docopt(__doc__, version='coinfund-cli 1.0')
  if args['vehicles']:
    print "VEHICLES"
