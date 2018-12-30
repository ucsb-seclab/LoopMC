
try:
    import IPython
except ImportError:
    pass

DEBUG_CALLS_TRACE = False
IMPRECISE_INVOKE_RESOLUTION = True

# Cache that holds resolved information, so if we query the same method we know the answer.
classifier_cache = {}

whitelisted_classes = [
    # DO NOT ADD ANYTHING HERE
]

whitelisted_packages = [
    # DO NOT ADD ANYTHING HERE
]

unlabelled_methods_fp = None

classes_label_map = {
    'Ljava/lang/Integer;': 'math',
    'Ljava/lang/Double;': 'math',
    'Ljava/util/BitSet;': 'math',
    'Ljava/lang/Math;': 'math',
    'Ljava/lang/Boolean;': 'math',
    'Ljava/lang/Float;': 'math',
    'Landroid/opengl/Matrix;': 'math',
    'Landroid/util/FloatMath;': 'math',
    'Ljava/lang/Byte;': 'math',
    'Ljava/lang/Long;': 'math',
    'Ljava/lang/Short;': 'math',
    'Ljava/lang/Number;': 'math',
    'Ljava/lang/StrictMath;': 'math',
    'Ljava/nio/ByteOrder;': 'math',
    'Ljava/nio/FloatBuffer;': 'math',
    'Landroid/graphics/Rect;': 'ui',
    'Landroid/graphics/RectF;': 'ui',
    'Landroid/graphics/Point;': 'ui',
    'Landroid/graphics/PointF;': 'ui',
    'Landroid/graphics/Color;': 'ui',
    'Landroid/graphics/Matrix;': 'ui',
    'Landroid/graphics/Path;': 'ui',
    'Landroid/graphics/Region;': 'ui',
    'Landroid/graphics/Picture;': 'ui',
    'Landroid/graphics/Bitmap;': 'ui',
    'Ljava/lang/StringBuffer;': 'string',
    'Ljava/lang/Character$UnicodeBlock;': 'string',
    'Ljava/lang/Character;': 'string',
    'Ljava/io/StringWriter;': 'string',
    'Ljava/io/StringBufferInputStream;': 'string',
    'Ljava/text/DecimalFormat;': 'string',
    'Ljava/text/NumberFormat;': 'string',
    'Landroid/text/format/DateFormat;': 'string',
    'Ljava/lang/StringBuilder;': 'string',
    'Ljava/lang/AbstractStringBuilder;': 'string',
    'Ljava/lang/String;': 'string',
    'Ljava/util/Formatter;': 'string',
    'Ljava/lang/Character;': 'string',
    'Ljava/lang/CharSequence;': 'string',
    'Ljava/nio/CharBuffer;': 'string',
    'Landroid/util/LruCache;': 'datastructure',
    'Landroid/util/Pair;': 'datastructure',
    'Landroid/util/TypedValue;': 'datastructure',
    'Ljava/util/Collection;': 'datastructure',
    'Ljava/util/Vector;': 'datastructure',
    'Ljava/util/Dictionary;': 'datastructure',
    'Ljava/util/HashMap;': 'datastructure',
    'Ljava/util/NavigableMap;': 'datastructure',
    'Ljavax/ws/rs/core/MultivaluedMap;': 'datastructure',
    'Ljava/util/SortedMap;': 'datastructure',
    'Ljava/util/SortedSet;': 'datastructure',
    'Ljava/util/HashSet;': 'datastructure',
    'Ljava/util/TreeSet;': 'datastructure',
    'Ljava/util/Set;': 'datastructure',
    'Ljava/util/NavigableSet;': 'datastructure',
    'Ljava/util/ArrayList;': 'datastructure',
    'Ljava/util/Map;': 'datastructure',
    'Ljava/util/Queue;': 'datastructure',
    'Ljava/util/Deque;': 'datastructure',
    'Ljava/util/List;': 'datastructure',
    'Ljava/util/LinkedList;': 'datastructure',
    'Ljava/nio/Buffer;': 'datastructure',
    'Ljava/nio/ByteBuffer;': 'datastructure',
    'Ljava/nio/DoubleBuffer;': 'datastructure',
    'Ljava/nio/FloatBuffer;': 'datastructure',
    'Ljava/nio/IntBuffer;': 'datastructure',
    'Ljava/nio/LongBuffer;': 'datastructure',
    'Ljava/nio/MappedByteBuffer;': 'datastructure',
    'Ljava/nio/ShortBuffer;': 'datastructure',
    'Landroid/util/MapCollections$ArrayIterator;': 'datastructure',
    'Landroid/util/MapCollections$MapIterator;': 'datastructure',
    'Landroid/util/MapCollections;': 'datastructure',
    'Ljava/util/Iterator;': 'iterator',
    'Ljava/util/Enumeration;': 'iterator',
    'Ljava/io/ObjectStreamField;': 'ioRead',
    'Ljava/io/StreamTokenizer;': 'ioRead',
    'Ljava/io/ByteArrayInputStream;': 'ioRead',
    'Ljava/io/ByteArrayOutputStream;': 'ioWrite'
}

# These are the classes that results in unnecessary transitive closure edges.
# for these classes we use the static type of invoke to get label
blacklisted_classes = {
    'Ljava/util/Map;'
}

packages_label_map = {
    'Ljava/math/': 'math',
    'Landroid/graphics/drawable/shapes/': 'ui',
    'Landroid/webkit/': 'webkit',
    'Landroid/drm/': 'drm',
    'Landroid/util/MapCollections$': 'datastructure',
    'Ljava/util/Map': 'datastructure'
}

irrelevant_packages = [
    'Landroid/test/',
    'Ljunit/',
    'Ljava/util/Currency'
]

white_listed_methods = []


def is_meth_in_cache(meth):
    global classifier_cache
    # key for classifier cache
    meth_key = meth.klass.class_name + ':' + str(meth.method_sign)
    # check cache
    if meth_key in classifier_cache:
        return (True, classifier_cache[meth_key])

    return (False, None)


def insert_meth_info_cache(meth, classification):
    global classifier_cache
    # key for classifier cache
    meth_key = meth.klass.class_name + ':' + str(meth.method_sign)
    # insert into classifier cache
    classifier_cache[meth_key] = classification


def is_klass_whitelisted(klass):
    global whitelisted_classes
    assert len(whitelisted_classes) == 0, 'Do not whitelist classes for ML project'
    assert len(whitelisted_packages) == 0, 'Do not whitelist packages for ML project'
    ret_val = klass.class_name in whitelisted_classes
    if not ret_val:
        ret_val = len(filter(lambda i: klass.class_name.startswith(i), whitelisted_packages)) > 0
    return ret_val


'''
    This method gets label from default mapping done for ML project.
'''


def get_ml_label(class_name):
    global classes_label_map
    global packages_label_map
    ret_val = None
    target_class_name = class_name
    if target_class_name.startswith('Landroid/support/v'):
        # print target_class_name
        # sys.exit(-1)
        target_class_name = 'Landroid' + target_class_name.split('Landroid/support/v')[1][1:]
    is_present = target_class_name in classes_label_map
    if is_present:
        ret_val = classes_label_map[target_class_name]
    if not ret_val:
        target_pkgs = filter(lambda i: target_class_name.startswith(i), packages_label_map)
        if len(target_pkgs) > 0:
            ret_val = packages_label_map[target_pkgs[0]]
    return ret_val


def is_klass_name_irrelevant(klass_name):
    global irrelevant_packages
    ret_val = len(filter(lambda i: klass_name.startswith(i), irrelevant_packages)) > 0
    return ret_val


def is_klass_irrelevant(klass):
    return is_klass_name_irrelevant(klass.class_name)


def is_klass_exception(klass):
    hierarchy_list = [x.class_name for x in klass.extends_ir]
    return 'Ljava/lang/Exception;' in hierarchy_list


def is_invoke_whitelisted(inv_ins):
    # If we have set of methods which need to be ignored.
    target_method_name = inv_ins.method_class_name + inv_ins.method_name
    ret_val = (target_method_name in white_listed_methods)

    # Or if the target method is constructing an exception.
    # TODO: Fix this, find a more robust way to say if an invoke is constructor or not.
    '''if not ret_val:
        ret_val = True
        for (tmp,tmp1,target_meth) in inv_ins.calls:
            if not is_klass_exception(target_meth.klass):
                ret_val = False
                break'''

    return ret_val



def get_apk_meth_label(meth, visited):
    global unlabelled_methods_fp
    ret_val = None
    if DEBUG_CALLS_TRACE:
        print('In get_apk_meth_label, Method:'+meth.method_name)
    target_label_traces = {}

    # on recursion, Sorry, I am out of F*#$!
    if meth in visited:
        return ret_val

    # if result is cached
    (is_found, ret_val) = is_meth_in_cache(meth)
    if is_found:
        return ret_val

    visited.append(meth)

    # get all the methods that could be called by current method
    for (called_meth_inv, tmp1, tmp2, called_meth) in meth.calls:
        # if the method is framework method, get its label
        if called_meth.klass.in_apk == False:
            if DEBUG_CALLS_TRACE:
                print('calling get_framework_method_label, with:'+str(called_meth_inv) + ', method:'+
                      called_meth.method_name)
            called_method_label = get_framework_method_label(called_meth_inv, called_meth)
            if called_method_label not in target_label_traces:
                target_label_traces[called_method_label] = []
            if called_meth not in target_label_traces[called_method_label]:
                if called_method_label == 'un_labelled':
                    if unlabelled_methods_fp is None:
                        unlabelled_methods_fp = open(os.path.basename(IRInstruction.ir_dex.apk_fp) + '_unlabelled_methods.txt', 'a+')
                    unlabelled_methods_fp.write(str(called_meth_inv) + ':CALLING:' + str(called_meth) + '\n')
                target_label_traces[called_method_label].append(called_meth)
        else:
            # else, get labels for the apk method
            if DEBUG_CALLS_TRACE:
                print('calling get_apk_meth_label, with:'+str(called_meth_inv) + ', method:'+
                      called_meth.method_name)
            called_method_label = get_apk_meth_label(called_meth, visited)
            if called_method_label != None:
                for (curr_label, curr_framemeth) in called_method_label:
                    if curr_label not in target_label_traces:
                        target_label_traces[curr_label] = []
                    if curr_framemeth not in target_label_traces[curr_label]:
                        target_label_traces[curr_label].append(curr_framemeth)

    ret_val = []

    # for each label, add one framework method
    for curr_label in target_label_traces:
        # if curr_label == 'un_labelled':
        # print 'FAIL:' + target_label_traces[curr_label][0].klass.class_name + ':' + target_label_traces[curr_label][0].method_sign
        ret_val.append((curr_label, target_label_traces[curr_label][0]))

    # insert into cache
    insert_meth_info_cache(meth, ret_val)
    del visited[-1]

    return ret_val


def get_first_level_apk_methods(invoke_ins):
    ret_val = []
    # Add all first level apk methods here
    for (tmp, tmp1, target_meth) in invoke_ins.calls:
        # if the current method is in apk
        if target_meth.klass.in_apk != False:
            # We consider only one directapk method needed to ml project
            ret_val.append((target_meth.klass.class_name, target_meth.method_sign, 'directapk', True))
            break
    return ret_val


def get_loop_body_info(self):
    loop_info = set()
    global unlabelled_methods_fp
    global DEBUG_CALLS_TRACE
    for curr_bb in self.loop_bbs:
        for invoke_ins in filter(lambda i: i.ins_ir_type == INS_INVOKE, curr_bb.inss):
            invoke_off = invoke_ins.offset
            if DEBUG_CALLS_TRACE:
                print('START: calling: get_invoke_targets_info')
            invoke_info = set(get_invoke_targets_info(invoke_ins))
            if DEBUG_CALLS_TRACE:
                print('END: end: get_invoke_targets_info')
            # prepend the invoke instruction offset
            invoke_info = set(map(lambda x: (invoke_off,) + x, invoke_info))
            loop_info.update(invoke_info)

            first_level_info = set(get_first_level_apk_methods(invoke_ins))
            first_level_info = set(map(lambda x: (invoke_off,) + x, first_level_info))
            loop_info.update(first_level_info)
    if unlabelled_methods_fp is not None:
        unlabelled_methods_fp.close()
        unlabelled_methods_fp = None
    return loop_info


# def get_loop_category(loop_obj):
# ret_val = 'benign'
# target_trace = None
# return_traces = []
##If a loop can invoke sdk method, then its malicious.
# for curr_bb in loop_obj.expanded_bbs:
# for invoke_ins in filter(lambda i:i.ins_ir_type == INS_INVOKE, curr_bb.inss):
# info = get_invoke_targets_info(invoke_ins)
# (is_suspi,target_trace) = can_invoke_sdk_meth(invo)
# return_traces.extend(target_trace)
# if is_suspi:
# ret_val = 'suspicious'

# return (return_traces,ret_val)

# reset the cache
def reset_classifier_cache():
    global classifier_cache
    classifier_cache = {}
    global white_listed_methods
    white_listed_methods = [line.strip() for line in open(os.environ["methods_white_list"])]
