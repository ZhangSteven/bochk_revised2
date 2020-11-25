# coding=utf-8

"""
For account 60001, they used a new cash report, holding report is the same.

This file contains functions to handle the new cash report.
"""
from bochk_revised.main import writeOutputCsv, getCashHeaders
from toolz.itertoolz import groupby
from toolz.functoolz import compose
from functools import partial
from datetime import datetime
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



"""
	[String] filename => [String] date (yyyy-mm-dd)

	filename is like: C:\\temp\\Cash Statement Report 27102020.csv
"""
getDateFromFilename = compose(
	lambda s: datetime.strptime(s, '%d%m%Y').strftime('%Y-%m-%d')
  , lambda s: s.split('.')[0][-8:]
  , lambda fn: fn.split('\\')[-1]
)



"""
	[String] filename => [List] cash entries to be written to csv file
"""
getCashEntries = lambda filename: \
	map( lambda L: L[0]
	   , groupby( lambda el: el['currency']
				, map( partial(toCashEntry, getDateFromFilename(filename))
					 , filter( lambda c: c['Remark'] == 'Closing balance'
							 , getPositions(filename)))
					 ).values()
	   )



"""
	[String] outputDir, [String] inputFile => [String] output csv file

	Convert input cash statement file to output cash csv file.
"""
write60001CashCsv = lambda outputDir, inputFile: writeOutputCsv( 
	outputDir
  , inputFile
  , '_bochk_' + getDateFromFilename(inputFile) + '_cash'
  , getCashHeaders()
  , getCashEntries(inputFile)
) 