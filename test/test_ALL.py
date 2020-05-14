# coding=utf-8
# 

import unittest2
from os.path import join
from bochk_revised2.cash import getCashFromActivity, getCashFromBalance
from bochk_revised2.main import getCurrentDirectory, fileToLines \
								, getCashFromBalancenActivityFiles
from utils.iter import firstOf



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



	def testGetCashFromBalancenActivityFiles(self):
		activityFile = join(getCurrentDirectory(), 'samples', 'Cash Stt _21042020_activity.xlsx')
		balanceFile = join(getCurrentDirectory(), 'samples', 'Cash Stt _21042020.xlsx')
		date, positions = getCashFromBalancenActivityFiles(balanceFile, activityFile)
		self.assertEqual('2020-04-21', date)
		positions = list(positions)
		self.assertEqual(3, len(positions))
		usd = firstOf(lambda p: p['currency'] == 'USD', positions)
		self.assertEqual('JIC INTERNATIONAL LIMITED - CLFAMC', usd['portfolio'])
		self.assertEqual('2020-04-21', usd['date'])
		self.assertAlmostEqual(207111.65, usd['balance'])

		hkd = firstOf(lambda p: p['currency'] == 'HKD', positions)
		self.assertAlmostEqual(579, hkd['balance'])

		eur = firstOf(lambda p: p['currency'] == 'EUR', positions)
		self.assertAlmostEqual(0, eur['balance'])