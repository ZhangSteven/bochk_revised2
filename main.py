# coding=utf-8
#
# BOCHK revised its cash report format, holding report not affected. We need to
# convert them to Geneva format for holding and cash reconciliation. Therefore
# we will use bochk_revised package to handle holding report, but handle cash
# report here.
# 


from os.path import join, dirname, abspath
import logging
logger = logging.getLogger(__name__)




if __name__ == '__main__':
	import logging.config
	logging.config.fileConfig('logging.config', disable_existing_loggers=False)

	