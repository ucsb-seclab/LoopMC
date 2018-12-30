from os.path import join, isfile, dirname
import sys
import os

# check methods labels file
methods_label_file = join(dirname(__file__), 'method_labels','interface_methods')
if not isfile(methods_label_file):
    raise Exception('Method label file not found at %s' % methods_label_file)

os.environ["methods_label_file"] = methods_label_file

class_method_label_file = join(dirname(__file__), 'method_labels','class_methods')
if not isfile(class_method_label_file):
    raise Exception('Object method label file not found at %s' % class_method_label_file)

os.environ["class_method_label_file"] = class_method_label_file

method_signature_label_file = join(dirname(__file__), 'method_labels','method_signature_label')
if not isfile(method_signature_label_file):
    raise Exception('Method signature label file not found at %s' % method_signature_label_file)

os.environ["method_signature_label_file"] = method_signature_label_file

from name_based_labelling import get_method_label_by_name
