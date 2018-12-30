'''
    This handles all the labelling support we need for loop_analysis.
'''

import os
from os.path import dirname, join
import sys
import re
from collections import defaultdict

    
from dfanalyzer import get_invoke_label
# TODO: Move instruction labelling here.

INVOKE_LOCAL_METHOD_TYPE = 'apk_method'
INVOKE_NON_LOCAL_METHOD_TYPE = 'lib_method'
INVOKE_SDK_METHOD_TYPE = 'sdk_method'
INVOKE_UNKNOWN_METHOD_TYPE = 'ambiguous_method'
INVOKE_UNRESOLVED_METHOD_TYPE = 'unresolved_method'

interface_methods_label = None
class_methods_label = None
method_signatures_label = None


def read_method_signatures_label():
    global method_signatures_label

    if not method_signatures_label:
        method_signatures_label = {}
        # read labels
        lines = [line.strip() for line in open(os.environ["method_signature_label_file"])]
        for curr_line in lines:
            if curr_line:
                parts = curr_line.split('=')
                if not parts[0] in method_signatures_label:
                    method_signatures_label[parts[0]] = {}
                method_signatures_label[parts[0]][parts[2]] = (int(parts[1]) == 1)


def get_method_signature_string_based_label(target_method_sign):
    global method_signatures_label

    read_method_signatures_label()

    ret_val = []
    if target_method_sign in method_signatures_label:
        for curr_lab in method_signatures_label[target_method_sign].keys():
            ret_val.append(curr_lab)

    return ret_val


def get_method_signature_based_label(target_method):
    return get_method_signature_string_based_label(target_method.method_sign)

