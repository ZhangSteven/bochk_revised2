# coding=utf-8

"""
For account 60001, they used a new cash report, holding report is the same.

This file contains functions to handle the new cash report.
"""
from toolz.itertoolz import groupby
from toolz.functoolz import compose
from functools import partial
import csv
import logging
logger = logging.getLogger(__name__)



def getPositions(filename):
	"""
	[String] filename => [List] positions
	"""
	with open(filename, newline='') as csvfile:
		return list(csv.DictReader(csvfile))



toFloatIfString = lambda s: \
	float(s) if isinstance(s, str) else s



"""
	[Dictionary] position => [Dictionary] cash entry
"""
toCashEntry = lambda date, position: \
	{ 'portfolio': position['Portfoio Code']
	, 'custodian': ''
	, 'date': date
	, 'currency': position['Cash Account Ccy']
	, 'balance': toFloatIfString(position['Cumm EFF On Cash Balance'])
	}



def getCashEntries(filename):
	"""
	[String] filename => [List] cash entries to be written to csv file
	"""
	getFirst = lambda L: L[0]

	currencyType = lambda el: el['currency']

	getDateFromFilename = lambda name: \
		'2020-11-20'


	return map( getFirst
		      , groupby( currencyType
		      		   , map( partial(toCashEntry, getDateFromFilename(filename))
			  				, filter( lambda c: c['Remark'] == 'Closing balance'
			  		  				, getPositions(filename)))
		      		   ).values()
		      )