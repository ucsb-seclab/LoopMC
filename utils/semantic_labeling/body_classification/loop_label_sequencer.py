__author__ = 'machiry'
def get_label_sequence(invoke_ins):
    ret_val = []
    target_framework_labels = {}
    if DEBUG_CALLS_TRACE:
        print('In get_label_sequence, for:'+str(invoke_ins))

    android_label = get_method_signature_based_label(invoke_ins)
    if len(android_label) > 0:
        ret_val.append(android_label[0])

    if is_invoke_whitelisted(invoke_ins):
        ret_val.append('invoke_whitelisted')
    else:
        # for each method that could be called,
        for (tmp, tmp1, target_meth) in invoke_ins.calls:
            if target_meth.klass.in_apk == False:
                # if its framework method, get its label
                if DEBUG_CALLS_TRACE:
                    print('calling get_label_sequence for:'+str(invoke_ins)+', by method:'+
                          str(target_meth.method_name))
                curr_meth_label = get_framework_method_label(invoke_ins, target_meth)
                ret_val.append(curr_meth_label)
            else:
                # if its apk method gets its labels
                if DEBUG_CALLS_TRACE:
                    print('calling get_apk_meth_label for:'+str(invoke_ins)+', by method:'+
                          str(target_meth.method_name))
                apk_meth_labels = get_apk_meth_label(target_meth, [])
                if apk_meth_labels and (len(apk_meth_labels) > 0):
                    for (curr_meth_label, target_framework_meth) in apk_meth_labels:
                        # We just need one method per label, So, ignore a method if we already found a method for a label
                        if curr_meth_label not in target_framework_labels:
                            target_framework_labels[curr_meth_label] = (target_framework_meth, False)

        if len(target_framework_labels) > 0:
            for curr_label in target_framework_labels:
                (curr_meth, direct_flag) = target_framework_labels[curr_label]
                ret_val.append((curr_meth.klass.class_name, curr_meth.method_sign, curr_label, direct_flag))
        else:
            # if there are no labels, that means no framework method can be called from this method.
            ret_val.append((invoke_ins.method_class_name, invoke_ins.method_sign, 'intra_apk', True))

    return ret_val