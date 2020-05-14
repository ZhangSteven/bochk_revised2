# coding=utf-8
# 

import unittest2
from os.path import join
from bochk_revised2.cash import getCashFromActivity, getCashFromBalance
from bochk_revised2.main import getCurrentDirectory, fileToLines



class TestAll(unittest2.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestAll, self).__init__(*args, **kwargs)



	def testGetCashFromActivity(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Stt _21042020_activity.xlsx')
		d = getCashFromActivity(fileToLines(file))
		self.assertEqual(1, len(d))
		self.assertEqual('USD', d['USD']['currency'])
		self.assertEqual('JIC INTERNATIONAL LIMITED - CLFAMC', d['USD']['portfolio'])
		self.assertAlmostEqual(207111.65, d['USD']['balance'])



	def testGetCashFromBalance(self):
		file = join(getCurrentDirectory(), 'samples', 'Cash Stt _21042020.xlsx')
		d = getCashFromBalance(fileToLines(file))
		self.assertEqual(3, len(d))
		self.assertEqual('HKD', d['HKD']['currency'])
		self.assertEqual('JIC INTERNATIONAL LIMITED - CLFAMC', d['HKD']['portfolio'])
		self.assertAlmostEqual(579, d['HKD']['balance'])
		self.assertAlmostEqual(0, d['EUR']['balance'])
		self.assertAlmostEqual(456330.61, d['USD']['balance'])