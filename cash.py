# coding=utf-8

"""
Since 2020 Apr, BOCHK revised its cash report format, holding report not affected.

This module handles the new format here. For each currency, then

	1) use cash activity report balance (day end balance);
	2) if not, use cash report (real time balance)

"""
from functools import partial, reduce
from itertools import takewhile, filterfalse
from toolz.functoolz import compose
from toolz.dicttoolz import valmap
from toolz.itertoolz import groupby as groupbyToolz
from utils.iter import pop
from clamc_datafeed.feeder import mergeDictionary
import logging
logger = logging.getLogger(__name__)



def lognContinue(msg, x):
	logger.debug(msg)
	return x



def getCashFromBalance(lines):
	"""
	[Iterable] lines
		=> [Dictionary] currency -> cash entry

	There can be multiple lines for a currency. We need to add up balances from
	all those lines to form the final balances for the currency.
	"""

	def consolidate(group):
		"""
		[List] group => [Dictionary] consolidated position

		group is a list of cash entries of the same currency, here we add up
		their amount
		"""
		p = group[0].copy()
		p['balance'] = sum(map(lambda p: p['balance'], group))
		return valmap(lambda v: removeBOM(v) if isinstance(v, str) else v, p)


	return compose(
		partial(valmap, consolidate)
	  , partial(groupbyToolz, lambda d: d['currency'])		
	  , getRawPositions
	  , lambda lines: lognContinue('getCashFromBalance(): start', lines)
	)(lines)



def getCashFromActivity(lines):
	"""
	[Iterable] lines (from the cash avtivity file)
		=> [Dictionary] currency -> cash entry
	
	There may be multiple activity lines for a currency. The latest activity
	has the most updated balance and it is the first activity line for that
	currency. The outcome is a series of cash entries, each entry is a dictioanry
	containing the keys (portfolio, currency, balance)
	"""

	"""
		Only keep the first entry for a currency. Remove the leading '\ufeff'
		character in its account name value, because sometimes due to utf-8
		encoding this character is there.
	"""
	def combinePositions(acc, el):
		return acc if el['currency'] in acc else \
		mergeDictionary( acc
					   , {el['currency']: valmap(lambda v: removeBOM(v) if isinstance(v, str) else v, el)}
					   )


	return compose(
		lambda positions: reduce(combinePositions, positions, {})
	  , getRawPositions
	  , lambda lines: lognContinue('getCashFromActivity(): start', lines)
	)(lines)



"""
	[Iterable] lines => [Iterable] positions (each position is a dictionary)

	Get the headers from the first line, then use that header and each subsequent
	line to form a position (Dictionary).
"""
def getRawPositions(lines):

	nonEmptyLine = lambda line: len(line) > 0 and line[0] != ''
	

	headerMap = {
		'Account Name': 'portfolio'
	  , 'Currency': 'currency'
	  , 'Currency(or Equiv.)': 'currency'
	  , 'Ledger Balance': 'balance'
	  , 'Ledger Balance(Total Equiv.)': 'balance'
	}


	"""
		[List] line => [List] Headers

		Only a few fields (headers) will be useful in the output csv, therefore 
		we map those headers to field names in the output csv.
	"""
	getHeadersFromLine = compose(
		list
	  , partial(map, lambda s: headerMap[s] if s in headerMap else s)
	  , partial(map, lambda s: s.split('\n')[-1])
	  , partial(takewhile, lambda s: s != '')
	)


	return \
	compose(
	 	partial(map, dict)
	  , lambda t: map(partial(zip, getHeadersFromLine(t[0])), t[1])
	  , lambda lines: (pop(lines), lines)
	  , partial(takewhile, nonEmptyLine)
	)(lines)



"""
	[String] s => [String] s

	Sometimes the values from the excel cells contains a leading '\ufeff' character,
	because of utf-8 encoding. We want to remove that character if it is there.
"""
removeBOM = lambda s: s[1:] if len(s) > 0 and s[0] == '\ufeff' else s
