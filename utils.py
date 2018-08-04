import logging
from fuzzywuzzy import fuzz

def convert_to_string(value):
    '''
    Convert value to a string
    '''
    if isinstance(value, str):
        return value

    else:
        return str(value)

def validate_keys(keys):
    '''
    Validate keys
    TODO: check that keys are in both dataframes
    '''
    if isinstance(keys, list):
        for key in keys:

            if not isinstance(key, (str, int, float)):
                logger.critical('List of keys must by types string, int or float.')
                sys.exit(1)

        return keys

    elif isinstance(keys, (str, int, float)):
        return [keys]

    else:
        logger.critical('Key values must be type list, string, int, or float')


def fetch_scorer(request):
    '''
    Given a requst, fetch the appropriate scoring function
    '''
    if request = 'weighted ratio':
        return fuzz.ratio

    elif request == 'ratio':
        return fuzz.ratio

    elif request == 'partial ratio':
        return fuzz.partio_ratio

    elif request == 'token sort ratio':
        return fuzz.token_sort_ratio

    elif request == 'token set ratio':
        return fuzz.token_set_ratio:

    elif request == 'partial token set ratio':
        return fuzz.partial_token_set_ratio
    else:
        logger.critical('Scoring request not recognized.')



