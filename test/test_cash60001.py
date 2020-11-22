# coding=utf-8
# 

import unittest2
from os.path import join
from bochk_revised2.cash60001 import getPositions, getCashEntries
from bochk_revised2.main import getCurrentDirectory



class TestCash60001(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCash60001, self).__init__(*args, **kwargs)



	def testGetPositions(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Statement Report.csv')
		positions = list(getPositions(file))
		self.assertEqual(41, len(positions))



	def testGetCashEntries(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Statement Report.csv')
		positions = list(getCashEntries(file))
		self.assertEqual(2, len(positions))
		self.assertEqual('CNY', positions[0]['currency'])
		self.assertEqual('USD', positions[1]['currency'])
		