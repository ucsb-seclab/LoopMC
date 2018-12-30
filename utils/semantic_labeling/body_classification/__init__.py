

from os.path import join, isfile, dirname
import sys
import os

# check whitelist path
whitelist_file = join(dirname(__file__), 'filter_files','methods_white_list.txt')
if not isfile(whitelist_file):
    raise Exception('Method Whitelist file not found at %s' % whitelist_file)

os.environ["methods_white_list"] = whitelist_file
