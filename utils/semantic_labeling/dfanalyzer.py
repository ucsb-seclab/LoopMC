
import sys

from os.path import abspath, dirname, isdir, join
import re
import traceback
import json
from ConfigParser import SafeConfigParser
from docopt import docopt
from collections import defaultdict

try:
    from clint.textui import colored
except:
    class Passthrough(object):
        def __getattr__(self, name):
            return lambda x: x
    colored = Passthrough()

import SignatureParser

TAGS = [
    '#browsehistoryuri',
    '#javascript',
    '#storagedelete',
    '#contentproviderdelete',
    '#contentresolverdelete',
    '#vibrator',
    '#aidl',
    '#alarm',
    '#reflection',
    '#audiostream',
    '#contacturi',
    '#identifier',
    '#process',
    '#bluetooth',
    '#abortbroadcast',
    '#sms',
    '#audio',
    '#phone',
    '#camera',
    '#contentprovider',
    '#contentresolver',
    '#location',
    '#networkconnect',
    '#crypto',
    '#storage',
    '#drawontop',
    '#genericIO',
    '#date',
    '#random',
    '#network',
    '#log',
    '#intent',
    '#resource',
]

signatures = None
field_signatures = None
whitelist = None


def get_invoke_label(ir_dex, target_ins, meth=None):
    global signatures
    if not signatures:
        flow_db_fp = abspath(join(dirname(__file__), 'conf', 'flow.db'))
        more_flow_db_fp = abspath(join(dirname(__file__), 'conf', 'more_flow.db'))
        field_signatures_fp = abspath(join(dirname(__file__), 'conf', 'field_signs.db'))
        whitelist_fp = abspath(join(dirname(__file__), 'conf', 'whitelist.db'))
        signatures = SignatureParser.getSignatures(flow_db_fp)
        more_signatures = SignatureParser.getSignatures(more_flow_db_fp)
        signatures.extend(more_signatures)
        field_signatures = parse_field_signatures(field_signatures_fp)
        whitelist = parse_whitelist(whitelist_fp)
    return handle_invoke(ir_dex, target_ins, signatures, meth=meth)


def handle_invoke(ir_dex, invoke, signatures, meth=None):
    if meth is not None:
        target_class_name = meth.klass.class_name
    else:
        target_class_name = invoke.method_class_name
    if target_class_name in ir_dex.classes_map:
        return check_invoke_against_signatures(ir_dex, invoke, signatures, meth=meth)
    return []


def handle_getfield(ir_dex, getfield_ins, signatures):
    if getfield_ins.field:
        return check_getfield_against_signatures(ir_dex, getfield_ins, signatures)
    return []


def check_invoke_against_signatures(ir_dex, invoke, signatures, meth=None):
    matches = []
    for signature in signatures:
        if check_invoke_against_signature(ir_dex, invoke, signature, meth=meth):
            matches.append(signature)
    return matches


def check_signature_match(target_signature, class_name, method_name, args):
    # remove ths support prefix, so that we can apply our generic matching
    if class_name.startswith('android.support.v'):
        # print 'GOT:' + class_name
        prts = class_name.split('android.support.v')
        # Remove the version string
        class_name = 'android.' + prts[1][2:]
        # print 'Changed:' + class_name
    return target_signature.match(class_name, method_name, args)


def check_invoke_against_signature(ir_dex, invoke, signature, meth=None):
    method_name = invoke.method_name
    idx = 0
    args = []
    while idx < len(invoke.args):
        arg = invoke.args[idx]
        args.append(arg)
        if arg in ['J', 'D']:
            idx += 2
        else:
            idx += 1
    args = map(raw_to_norm_type, args)

    if meth is not None:
        target_class_name = meth.klass.class_name
    else:
        target_class_name = invoke.method_class_name
        
    klass = ir_dex.classes_map[target_class_name]
    for c in [klass] + klass.extends_ir + klass.implements_ir:
        class_name = raw_to_norm_type(c.class_name)
        if check_signature_match(signature, class_name, method_name, args):
            return True
    return False


def check_getfield_against_signatures(ir_dex, getfield_ins, signatures):
    matches = []
    for signature in signatures:
        if check_getfield_against_signature(ir_dex, getfield_ins, signature):
            matches.append(signature)
    return matches


def check_getfield_against_signature(ir_dex, getfield_ins, field_signature):
    tag, sign_class_name, sign_field_name = field_signature
    if sign_class_name != getfield_ins.field.class_name:
        return False
    if sign_field_name != getfield_ins.field.field_name:
        return False
    return True


def check_class_against_whitelist(class_name, whitelist):
    for entry in whitelist:
        if re.match(entry, class_name):
            return True
    return False


def process_matches(matches, out_f, json_f):
    from core.ir.IRInstruction import INS_INVOKE, INS_GET
    print colored.green('Found %s sensitive matches' % len(matches))
    entries = defaultdict(list)
    for ins, matches in matches:
        if ins.ins_ir_type == INS_INVOKE:
            invoke = ins
            offset = hex(invoke.offset)
            caller = '%s:%s' % (invoke.method.class_name, invoke.method.method_sign)
            callee = '%s:%s' % (invoke.method_class_name, invoke.method_sign)
            for match in matches:
                tag = '#%s' % match.tags[0]
                entry = (tag, offset, caller, callee, str(match))
                priority = get_tag_priority(tag)
                entries[priority].append(entry)
        elif ins.ins_ir_type == INS_GET:
            getfield_ins = ins
            offset = hex(getfield_ins.offset)
            caller = str(getfield_ins.method)
            
            #the format of caller is not correct:
            #Lclass/class/method(params)return;
            #we want: Lclass/class;:method(params)return;
            other, params_and_return = caller.split("(")
            params_and_return = "(" + params_and_return
            class_name, sep, method_name = other.rpartition("/")
            caller = class_name  + ";:" + method_name + params_and_return
            #print "+++", caller
            
            field_desc = str(getfield_ins.field)
            for match in matches:
                tag = match[0]
                entry = (tag, offset, caller, field_desc, str(match))
                priority = get_tag_priority(tag)
                entries[priority].append(entry)

    json_entries = []
    for priority, entries in sorted(entries.items()):
        for entry in entries:
            #print "***",entry[2]
            out_f.write('%s\n' % str(entry))
            if json_f:
                dentry = {
                    'tag': entry[0],
                    'offset': entry[1],
                    'caller_class_name': entry[2].split(':')[0],
                    'caller_method_sign': entry[2].split(':')[1],
                    'instruction': entry[3],
                    'signature': entry[4]}
                json_entry = json.dumps(dentry)
                json_entries.append(json_entry)
    if json_f:
        json_output = '[' + ','.join(json_entries) + ']'
        json_f.write(json_output)


def get_tag_priority(tag):
    if tag in TAGS:
        return TAGS.index(tag)
    return -1


def parse_field_signatures(field_signatures_fp):
    # #something classname LASD; field
    field_signatures = []
    for line in open(field_signatures_fp).read().split('\n'):
        if not line:
            continue
        tag, class_name, field_name = line.split(' ')
        field_signatures.append((tag, class_name, field_name))
    return field_signatures


def parse_whitelist(whitelist_fp):
    whitelist = []
    for line in open(whitelist_fp).read().split('\n'):
        if not line:
            continue
        whitelist.append(line)
    return whitelist


def raw_to_norm_type(raw_type):
    raw_to_norm_type_map = {'V': 'void',
                            'B': 'byte',
                            'C': 'char',
                            'D': 'double',
                            'F': 'float',
                            'I': 'int',
                            'J': 'long',
                            'S': 'short',
                            'Z': 'boolean'}

    if raw_type[0] in raw_to_norm_type_map:
        return raw_to_norm_type_map[raw_type]
    elif raw_type[0] == 'L':
        return raw_type[1:-1].replace('/', '.')
    elif raw_type[0] == '[':
        return raw_to_norm_type(raw_type[1:]) + '[]'
    else:
        raise Exception('Not valid raw_type: %s' % raw_type)
