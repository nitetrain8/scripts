"""

Created by: Nathan Starkweather
Created on: 02/07/2014
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from os import stat

from datetime import datetime
result = stat(__file__)


# date = datetime.fromordinal(result.st_mtime)
print(datetime.fromtimestamp(int(result.st_mtime)))

