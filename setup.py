# -*- coding: utf-8 -*-
# @Author: Jake Brukhman
# @Date:   2016-07-01 11:17:50
# @Last Modified by:   Jake Brukhman
# @Last Modified time: 2016-07-01 12:01:53

from distutils.core import setup

setup(
    name='coinfund-cli',
    version='1.0',
    description='CoinFund Command-Line Interface',
    author='Jake Brukhman',
    author_email='jake@coinfund.io',
    url='https://github.com/coinfund/coinfund-cli',
    packages=['coinfund'],
    scripts=['bin/cf.py'],
    install_requires=[
      'docopt',
      'pyyaml'
    ]
)