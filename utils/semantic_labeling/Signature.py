import re

class Signature:

    def __init__(self, parsed_sig):
        ps = parsed_sig.asDict()
        #IPython.embed()

        #removing all the stupid stuff returned from the parser
        self.class_name = ps['class_name'][1]
        self.class_regex = False
        if self.class_name.startswith('*'):
            self.class_name = self.class_name[1:]
            self.class_regex = True
        self.method_name = ps['method_name']
        self.method_regex = False
        if self.method_name.startswith('*'):
            self.method_regex = True
            self.method_name = self.method_name[1:]
        arg_list = []
        self.args = []
        self.ignore_args = False
        if 'parameters' in ps:
            if not isinstance(ps['parameters'], list):
                self.ignore_args = True
            else:
                for p in ps['parameters']:
                    par = p[0][-1]
                    self.args.append(par)
        self.ret_type = ps['return_type'][-1]
        if 'tags' in ps:
            self.tags = [t[1] for t in ps['tags']]
        else:
            self.tags = ['genericIO']
        assert len(self.tags) == 1

    def match(self, class_name, method_name, args):
        class_name = class_name.split('$')[0]
        if self.class_regex:
            match = re.match(self.class_name,class_name)
            if not match:
                return False
        elif self.class_name != class_name:
            return False

        if self.method_regex:
            match = re.match(self.method_name,method_name)
            if not match:
                return False
        elif self.method_name != method_name:
            return False
        if (not self.ignore_args):
            if (len(self.args) != len(args)):
                return False
            for larg, rarg in zip(self.args, args):
                if larg != rarg:
                    return False
        return True

    def __str__(self):
        tstr = ""
        tstr += '#%s' % self.tags[0] + " "
        tstr += self.ret_type + " "
        tstr += self.class_name + ":"
        tstr += self.method_name
        tstr += "(" + ",".join(self.args) + ")"
        return tstr
