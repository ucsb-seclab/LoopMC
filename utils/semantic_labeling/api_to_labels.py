import os,sys,re
sys.path.append("..")
from name_based_labelling import check_method_label_by_name

package_re = re.compile("package (.*) {")
class_re = re.compile(  "  .*class (\S+) .*{")
intfc_re = re.compile(  "  .*interface (\S+) .*{")
ctor_re =  re.compile(  "    ctor .* (\S+\(.*\)).*;")
method_re = re.compile( "    method.* (\S+) (\S+\(.*\)).*;")
field_re = re.compile(  "    field .*;")
enum_re = re.compile(   "    enum_constant .*;")
end_cls_re = re.compile("  }")
end_pkg_re = re.compile("}")


curstack = []

new_only = False

with open(sys.argv[1]) as f:
    lines = f.readlines()

def norm_to_raw_type(norm_type):
	norm_to_raw_type_map = {'void': 'V',
							'byte': 'B',
							'char': 'C',
							'double': 'D',
							'float': 'F',
							'int': 'I',
							'long': 'J',
							'short': 'S',
							'boolean': 'Z'}
	raw_type = None
	is_array = False
	if norm_type[-1] == ']':
		is_array = True
		norm_type = norm_type[:-2]
	if norm_type in norm_to_raw_type_map.keys():
	    raw_type = norm_to_raw_type_map[norm_type]
	else:
	    raw_type = "L" + norm_type.replace('.', '/') + ";"
	if is_array:
	    raw_type += '[]'
	return raw_type

sig_re = re.compile("(\S+)\((.*)\);*")
def make_signature(original_sig, ret_type, is_ctor=False):
	parsed = sig_re.match(original_sig)
	if not parsed:
		raise RuntimeError("Incorrect signature format: " + original_sig)
	orig_types = parsed.group(2)
	new_ret_type = norm_to_raw_type(ret_type)
	if not orig_types.strip():
		# Void!
		types = ['V']
	else:
		types = [norm_to_raw_type(t) for t in orig_types.split(", ")]
	if is_ctor:
		mname = "<init>"
	else: 
		mname = parsed.group(1)
	sig = "%s(%s)%s" % (mname,", ".join(types), new_ret_type)
	return sig, mname


package = "None"
cls = "None"
for line in lines:

    # is it new?
    if line.startswith("+"):
        isNew = True
        realline = line.lstrip("+")
    elif line.startswith("-"):
        isNew = False 
        realline = line.lstrip("-")
    else:
        isNew = False
        realline = line
    if not realline.strip():
        continue    
    if package_re.match(realline):
        package = package_re.match(realline).group(1)
    elif class_re.match(realline):
        cls = class_re.match(realline).group(1)
    elif field_re.match(realline):
        pass # Fuck fields
    elif intfc_re.match(realline):
        pass # Fuck interfaces
    elif enum_re.match(realline):
        pass # Fuck interfaces
    elif method_re.match(realline):
    	parsed = method_re.match(realline)
    	if not realline:
    		raise RuntimeError("OW")
    	realcls = norm_to_raw_type(package + "." + cls)
    	sig,mname = make_signature(parsed.group(2),parsed.group(1))
    	#print mname, realcls, sig
        label = check_method_label_by_name(mname, realcls, sig)
        print "%s.%s -> %s" % (realcls, sig, label)
    elif ctor_re.match(realline):
    	parsed = ctor_re.match(realline)
    	realcls = norm_to_raw_type(package + "." + cls)
    	sig,mname = make_signature(parsed.group(1),"V", is_ctor=True)
    	#print mname, realcls, sig
        label = check_method_label_by_name(mname, realcls, sig)
        print "%s.%s -> %s" % (realcls, sig, label)

    elif end_pkg_re.match(realline):
        package = "None"
    elif end_cls_re.match(realline):
        cls = "None"
    else:
        raise RuntimeError("Couldn't match line: " + realline)

