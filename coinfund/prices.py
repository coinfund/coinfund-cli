import cryptocompare

from decimal import Decimal

class Price(object):
  
  def __init__(self):
  	pass

  def of(self, instr):
	  data = cryptocompare.get_price(instr, curr='USD')
	  return Decimal(data[instr]['USD'])