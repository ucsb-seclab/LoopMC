from label_utils import get_method_signature_string_based_label
from body_classification.loop_body_classifier import is_klass_name_irrelevant, get_ml_label
import dfanalyzer


def check_method_label_by_name(method_name, class_name, method_signature):

    """
        This method checks whether the given method had label.

        Example: get_method_label_by_name('equals', 'Ljava/lang/Object;', 'equals(Ljava/lang/Object;)Z')
        True

    :param method_name: Name of the method Ex: 'equals'
    :param class_name: Class name in java form Ex: 'Ljava/lang/Object;'
    :param method_signature: Signature of the method in java form Ex: 'equals(Ljava/lang/Object;)Z'
    :return: True if label exists else False

    """

    ret_val = get_method_signature_string_based_label(method_signature)
    if len(ret_val) > 0:
        return True
    if is_klass_name_irrelevant(class_name):
        return True
    if get_ml_label(class_name):
        return True
    try:
        dfanalyzer.get_invoke_label(None, None)
    except Exception as e:
        pass
    for curr_sig in dfanalyzer.signatures:
        if dfanalyzer.check_signature_match(curr_sig, dfanalyzer.raw_to_norm_type(class_name), method_name, []):
            return True
    return False


def get_method_label_by_name(method_name, class_name, method_signature):

    """
        This method gets a label (if exists) for the provided method.

        Example: get_method_label_by_name('equals', 'Ljava/lang/Object;', 'equals(Ljava/lang/Object;)Z')
        ObjectComparision

    :param method_name: Name of the method Ex: 'equals'
    :param class_name: Class name in java form Ex: 'Ljava/lang/Object;'
    :param method_signature: Signature of the method in java form Ex: 'equals(Ljava/lang/Object;)Z'
    :return: Label name if exists else None

    """

    ret_val = get_method_signature_string_based_label(method_signature)
    if len(ret_val) > 0:
        return ret_val[0]
    if is_klass_name_irrelevant(class_name):
        return "nolabel"
    ml_lab = get_ml_label(class_name)
    if ml_lab:
        return ml_lab
    try:
        invok_lab = dfanalyzer.get_invoke_label(None, None)
        if invok_lab and len(invok_lab) > 0:
            return invok_lab[0].tags[0]
    except Exception as e:
        pass
    for curr_sig in dfanalyzer.signatures:
        if dfanalyzer.check_signature_match(curr_sig, dfanalyzer.raw_to_norm_type(class_name), method_name, []):
            return curr_sig.tags[0]
    return None


