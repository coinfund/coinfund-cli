# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:17:50
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-12-27 12:30:13

from distutils.core import setup

setup(
    name='coinfund-cli',
    version='1.1',
    description='CoinFund Command-Line Interface',
    author='Jake Brukhman',
    author_email='jake@coinfund.io',
    url='https://github.com/coinfund/coinfund-cli',
    packages=['coinfund'],
    scripts=['bin/cf'],
    install_requires=[
      'docopt',
      'pyyaml',
      'psycopg2',
      'sqlalchemy',
      'tabulate',
      'alembic',
      'inflection',
      'pandas',
      'numpy',
      'cryptocompare'
    ]
)