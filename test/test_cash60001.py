# coding=utf-8
# 

import unittest2
from os.path import join
from bochk_revised2.cash60001 import getPositions, getCashEntries \
									, write60001CashCsv
from bochk_revised2.main import getCurrentDirectory



class TestCash60001(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCash60001, self).__init__(*args, **kwargs)



	def testGetPositions(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Statement Report 27102020.csv')
		positions = list(getPositions(file))
		self.assertEqual(41, len(positions))



	def testGetCashEntries(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Statement Report 27102020.csv')
		positions = list(getCashEntries(file))
		self.assertEqual(2, len(positions))
		self.assertEqual('CNY', positions[0]['currency'])
		self.assertEqual('USD', positions[1]['currency'])

		self.assertAlmostEqual(233068.72, positions[0]['balance'])
		self.assertEqual('2020-10-27', positions[0]['date'])
		self.assertEqual('ABC FUND', positions[0]['portfolio'])



	def testOutputCashCsv(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Statement Report 27102020.csv')
		outputCsv = write60001CashCsv(
			join(getCurrentDirectory(), 'samples')
		  , file
		)
		self.assertEqual( 'samples_bochk_2020-10-27_cash.csv'
						, outputCsv.split('\\')[-1]
						)