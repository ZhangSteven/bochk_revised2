# coding=utf-8

"""
Since 2020 Apr, BOCHK revised its cash report format, holding report not affected.

Therefore we will use bochk_revised package to handle holding report, but handle 
cash with a new set of logic here.
"""
from bochk_revised2.cash import getCashFromBalance, getCashFromActivity
from bochk_revised.main import writeHoldingCsv, writeOutputCsv, getCashHeaders
from clamc_datafeed.feeder import fileToLines, mergeDictionary
from toolz.functoolz import compose
from toolz.itertoolz import groupby as groupbyToolz
from functools import partial, reduce
from itertools import chain, filterfalse
from datetime import datetime
from os.path import join, dirname, abspath
import logging, re
logger = logging.getLogger(__name__)



def lognRaise(msg):
	logger.error(msg)
	raise ValueError


def lognContinue(msg, x):
	logger.debug(msg)
	return x



def doOutput(outputDir, inputFiles):
	"""
	[String] outputDir (the directory to write output csvs to)
	[Iterable] inputFiles
		=> ( [Iterable] successful input files
		   , [Iterable] output csv files
		   )

	Side effect: write output csv files to the output directory
	"""
	logger.debug('doOutput(): start')

	isHoldingFile = lambda file: 'holding' in stripFilePath(file).lower()


	splitCashnHolding = lambda acc, el: \
		(acc[0] + [el], acc[1]) if isHoldingFile(el) else \
		(acc[0], acc[1] + [el])


	combineResult = lambda successfulHoldingFiles, holdingCsvFiles \
							, successfulCashFiles, cashCsvFiles: \
		( chain(successfulHoldingFiles, successfulCashFiles)
		, chain(holdingCsvFiles, cashCsvFiles)
		)


	return compose(
		lambda t: combineResult( *doOutputHolding(outputDir, t[0])
							   , *doOutputCash(outputDir, t[1])
							   )
	  , lambda _, inputFiles: reduce(splitCashnHolding, inputFiles, ([], []))
	)(outputDir, inputFiles)



def doOutputCash(outputDir, inputFiles):
	"""
	[String] outputDir (the directory to write output csvs to)
	[Iterable] inputFiles
		=> ( [Iterable] successful input files
		   , [Iterable] output csv files
		   )

	Side effect: write output csv files to the output directory

	Assume inputFiles is only cash files (balance or activity files)
	"""
	logger.debug('doOutputCash(): start')

	def canGetDateFromFileName(file):
		try:
			getDateFromFileName(file)
			return True
		except:
			logger.warning('doOutputCash(): failed to get date from file name: {0}'.format(file))
			return False


	"""
		[List] t (a list with two file names)
			=> [Tuple] t (balance file, activity file) or
						 ('', '') if the input files do not contain just one
						 balance file and one activity file
	"""
	toOrderedGroup = lambda t: \
		(t[1], t[0]) if isActivityFile(t[0]) and not isActivityFile(t[1]) else \
		(t[0], t[1]) if isActivityFile(t[1]) and not isActivityFile(t[0]) else \
		('', '')


	"""
		[String] outputDir, [Tuple] t (balance file, activity file)
			=> [String] output cash csv

		Side effect: write the cash csv file if successful
	"""
	def toCashOutputCsv(outputDir, t):
		try:
			return writeCashCsv(outputDir, t[0], t[1])
		except:
			return ''


	isActivityFile = lambda fn: 'activity' in stripFilePath(fn).lower()


	accumulate = lambda acc, el: \
		(chain(acc[0], el[0]), acc[1] + [el[1]])


	return compose(
		lambda groupResults: reduce(accumulate, groupResults, ([], []))
	  , lambda groups: map( lambda t: (t, toCashOutputCsv(outputDir, t))
						  , groups)
	  , partial(filterfalse, lambda group: group == ('', ''))
	  , partial(map, toOrderedGroup)
	  , partial(filter, lambda group: len(group) == 2)
	  , lambda d: d.values()
	  , partial(groupbyToolz, getDateFromFileName)
	  , lambda _, inputFiles: filter(canGetDateFromFileName, inputFiles)
	)(outputDir, inputFiles)
	


def doOutputHolding(outputDir, inputFiles):
	"""
	[String] outputDir (the directory to write output csvs to)
	[Iterable] inputFiles
		=> ( [Iterable] successful input files
		   , [Iterable] output csv files
		   )

	Side effect: write output csv files to the output directory

	Assume inputFiles is only holding files
	"""
	logger.debug('doOutputHolding(): start')

	def toHoldingOutputCsv(outputDir, file):
		try:
			return writeHoldingCsv(outputDir, file)
		except:
			logger.exception('toHoldingOutputCsv(): ')
			return ''


	accumulate = lambda acc, el: (acc[0] + [el[0]], acc[1] + [el[1]])


	return compose(
		lambda results: reduce(accumulate, results, ([], []))
	  , partial(filter, lambda t: t[1] != '')
	  , lambda outputDir, inputFiles: \
	  		map( lambda fn: (fn, toHoldingOutputCsv(outputDir, fn))
	  		   , inputFiles)
	)(outputDir, inputFiles)



def getCashFromBalancenActivityFiles(balanceFile, activityFile):
	"""
	[String] balanceFile, [String] activityFile
		=> ( [String] date
		   , [Iterable] cash entries
		   )
	"""
	checkFileDates = compose(
		lambda t: lognRaise('checkFileDates(): inconsistant dates from filenames') \
						if t[0] != t[1] else t[0]
	  , lambda file1, file2: ( getDateFromFileName(file1)
	  						 , getDateFromFileName(file2)
	  						 )
	)


	processFiles = lambda date, balFile, actFile: compose(
		partial(map, partial(mergeDictionary, {'date': date, 'custodian':''}))
	  , lambda d: d.values()
	  , lambda _1, balFile, actFile: \
	  		mergeDictionary( getCashFromBalance(fileToLines(balFile))
					   	   , getCashFromActivity(fileToLines(actFile))
					   	   )
	)(date, balFile, actFile)


	return compose(
		lambda date: ( date
					 , processFiles(date, balanceFile, activityFile)
					 )
	  , lambda _: checkFileDates(balanceFile, activityFile)
	  , lambda _1, _2: lognContinue('getCashFromBalancenActivityFiles(): {0}, {1}'.format(balanceFile, activityFile), 0)
	)(balanceFile, activityFile)



""" 
	[String] fn (file name with path) => [String] file name without path
	
	Assume: file path is Windows style, i.e., using '\' as the spliter
"""
stripFilePath = lambda fn: fn.split('\\')[-1]



"""
	[String] file => [String] date (yyyy-mm-dd)

	The file looks like:

	C:\\bochk_revised2\\samples\\Cash Stt _21042020_activity.xlsx

	or,

	C:\\bochk_revised2\\samples\\Cash Stt _21042020.xlsx
"""
getDateFromFileName = compose(
	lambda s: datetime.strftime(datetime.strptime(s, '%d%m%Y'), '%Y-%m-%d')
  , lambda m: lognRaise('getDateFromFileName(): failed to get date from name') \
  				if m == None else m.group(1)
  , lambda s: re.match('.*(\d{8})', s)
  , stripFilePath
  , lambda file: lognContinue('getDateFromFileName(): {0}'.format(file), file)
)



"""
	Get the absolute path to the directory where this module is in.

	This piece of code comes from:

	http://stackoverflow.com/questions/3430372/how-to-get-full-path-of-current-files-directory-in-python
"""
getCurrentDirectory = lambda: dirname(abspath(__file__))



"""
	[String] cash balance file, [String] cash activity file, [String] output dir
		=> [String] output csv file name

	Side effect: write output csv file into the output directory
"""
writeCashCsv = lambda outputDir, balanceFile, activityFile: compose(
	lambda t: writeOutputCsv( outputDir
							, balanceFile
							, '_bochk_' + t[0] + '_cash'
							, getCashHeaders()
							, t[1]
							) 
  , lambda _, balanceFile, activityFile: \
  		getCashFromBalancenActivityFiles(balanceFile, activityFile)
)(outputDir, balanceFile, activityFile)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	file1 = join(getCurrentDirectory(), 'samples', 'Holding _12052020.xlsx')
	file2 = join(getCurrentDirectory(), 'samples', 'Wrong Holding _07052020.xlsx')
	file3 = join(getCurrentDirectory(), 'samples', 'Holding _17102019.xlsx')
	file4 = join(getCurrentDirectory(), 'samples', 'Cash Stt _16042020_activity.xlsx')
	file5 = join(getCurrentDirectory(), 'samples', 'Cash Stt _21042020.xlsx')
	file6 = join(getCurrentDirectory(), 'samples', 'Cash Stt _21042020_activity.xlsx')
	file7 = join(getCurrentDirectory(), 'samples', 'Cash Stt _13052020_activity.xlsx')
	file8 = join(getCurrentDirectory(), 'samples', 'Cash Stt _13052020.xlsx')
	file9 = join(getCurrentDirectory(), 'samples', 'Cash Stt _04212020 -Wrong Date.xlsx')

	successfulFiles, outputCsvs = doOutput(
		join(getCurrentDirectory(), 'samples')
	  , [file1, file2, file3, file4, file5, file6, file7, file8, file9]
	)
	print('\n{0} successful files'.format(len(list(successfulFiles))))
	print('Output CSVs:\n' + '\n'.join(list(outputCsvs)))