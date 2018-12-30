
#from MethodSignature import MethodSignature



from pyparsing import\
    alphas,Word, Optional, OneOrMore, Group, ParseException, ZeroOrMore, Or, Group, delimitedList, nums, printables, dblSlashComment, \
    CharsNotIn, oneOf

#from postprocess_utils import db_to_java_for_reflection_type, get_bytecode_type

import pprint
from Signature import Signature


def debug_db_data(content,result):
    print(repr(result))

    class Dummy:
        pass

    signature_list = []
    for i,t in enumerate(result):
        print "\n--- Signature %d ---"%i
        print t.tags
        print t.return_type
        print t.class_name
        print t.method_name
        tmp = Dummy()
        tmp.tags = t.tags
        tmp.return_type = t.return_type
        tmp.class_name = t.class_class
        tmp.method_name = t.method_name
        tmp.parameters = t.parameters
        for p in t.parameters:
            print "\t", p
        tmp.constraint_instruction_list = []

        signature_list.append(tmp)

    constrained_type_dict = {}
    for t in signature_list:
        for constrained_type,constraint_conversion_type in t.constraint_instruction_list:
            if(constrained_type not in constrained_type_dict):
                constrained_type_dict[constrained_type] = set()
            constrained_type_dict[constrained_type].add(constraint_conversion_type)

    for k,v in sorted(constrained_type_dict.iteritems()):
        print k.ljust(60),
        print v

    for k,v in sorted(constrained_type_dict.iteritems()):
        print '\t\tsignature_type_list.add("%s");' % db_to_java_for_reflection_type(k)

    print content.count("{"),content.count("}")


def getSignatures(signatureFile):
    fp = open(signatureFile,"rb")
    content = fp.read()
    fp.close()

    litteral = Word(alphas + nums + "_")
    regex_pattern = CharsNotIn("(")
    tags = (OneOrMore(Group('#' + litteral))).setResultsName("tags")
    hierarchy_modifier = oneOf("<= =")
    java_type = Group(Optional(hierarchy_modifier) + Word(alphas + nums + "_" + "." + "[" + "]" + "$"))
    return_type = (java_type | "*").setResultsName("return_type")
    method_name = (litteral | "<init>" | regex_pattern ).setResultsName("method_name")
    parameter = Group((java_type + litteral))
    parameter_list = (delimitedList(parameter) | "*").setResultsName("parameters")
    body_instruction = (CharsNotIn("{;}"))
    signature_body = (delimitedList(body_instruction,";")).setResultsName("signature_body")
    class_name = (java_type | Group(Optional(hierarchy_modifier) + CharsNotIn(":")) ).setResultsName("class_name")

    signature_stmt =    Group((Optional(tags) + return_type + class_name+":"+method_name+ \
                        "(" + Optional(parameter_list) + ")"+"{"+Optional(signature_body)+"}"))
    grammar = OneOrMore(signature_stmt)

    grammar.ignore(dblSlashComment)
    result = grammar.parseString(content)

    #IPython.embed()
    #debug_db_data(content,result)

    signatures = [Signature(sig) for sig in result]

    return signatures



if __name__ == "__main__":
    signatures = getSignatures("flow.db")
    for sig in signatures:
        print sig






