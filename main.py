# coding=utf-8

"""
Since 2020 Apr, BOCHK revised its cash report format, holding report not affected.

Therefore we will use bochk_revised package to handle holding report, but handle 
cash with a new set of logic here.
"""
from bochk_revised2.cash import getCashFromBalance, getCashFromActivity
from clamc_datafeed.feeder import fileToLines
from toolz.functoolz import compose
from datetime import datetime
from os.path import join, dirname, abspath
import logging
logger = logging.getLogger(__name__)



def lognRaise(msg):
	logger.error(msg)
	raise ValueError


def lognContinue(msg, x):
	logger.debug(msg)
	return x



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
  , lambda file: file.split('\\')[-1]
  , lambda file: lognContinue('getDateFromFileName(): {0}'.format(file), file)
)



"""
	Get the absolute path to the directory where this module is in.

	This piece of code comes from:

	http://stackoverflow.com/questions/3430372/how-to-get-full-path-of-current-files-directory-in-python
"""
getCurrentDirectory = lambda: dirname(abspath(__file__))




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	