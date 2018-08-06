def convert_to_string(value):
    '''
    Convert value to a string
    '''
    if isinstance(value, str):
        return value

    else:
        return str(value)

def convert_to_list(item):
    '''
    Check if item is a list
    If it isn't make it one
    '''
    if isinstance(item, list):
        return value
    else:
        return [value]

def cartesian_product(list1, list2):
    '''
    Get the Cartesian product of two lists
    '''
    
    list1 = convert_to_list(list1)
    list2 = convert_to_list(list2)
    pairs = []

    for item1 in list1:
        for item2 in list2:
            pair = [item1, item2]
            pairs.append(pair)

    return pairs
