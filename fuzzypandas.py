import logging
import pandas as pd
from fuzzywuzzy import fuzz


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def convert_to_string(value):
    '''
    Convert non-string values to strings
    '''
    if isinstance(value, str):
        return value
    else:
        return str(value)


def convert_to_list(value):

    if isinstane(value, list):
        return value
    else:
        return [value]


def score_pairs(data, match_data, keys):
    '''
    For each row of data in data
    data and match_data should be input as list of dicts
    '''
    combos = len(data) * len(match_data) * len(keys)
    logger.info('Starting Pair Scoring for {n} combinations.'.format(n=combos))

    pairs  = []
    score_cache = {}

    for row in data:
        for match_row in match_data:
            pair = {}
            sum_scores = 0

            for i, key in enumerate(keys, start=1):
   
                pair_string = '_'.join(sorted([row[key], match_row[key]]))

                if pair_string in score_cache:
                    score = score_cache[pair_string]

                else:
                    score = fuzz.WRatio(row[key], match_row[key])  # may want to replace with something else later
                    score_cache[pair_string] = score

                sum_scores += score
                avg_score = sum_scores / i

                pair[key] = row[key]
                pair['{col}_matched'.format(col=key)] = match_row[key]
                pair['{col}_match_score'.format(col=key)] = score
                pair['avg_match_score'] = avg_score

            pairs.append(pair) 

    logger.info('Completed pair matching.')
    return pairs


def matcher(a, b, on, score_cutoff):
    '''
    Get best matches
    '''
    pairs = score_pairs(data=a.to_dict('records'),
                        match_data=b.to_dict('records'),
                        keys=on)
    pairs = pd.DataFrame(pairs)

    pairs.sort_values(by=on + ['avg_match_score'],
                      ascending=[True] * len(on) + [False],
                      inplace=True)
    pairs.drop_duplicates(on, inplace=True)

    pairs = pairs[pairs.avg_match_score >= score_cutoff].copy()

    return pairs

    
def fuzzy_merge(a, b, on, how='left', score_cutoff=60):
    '''
    Fuzzy match dataframe a onto dataframe b
    '''
    matches = matcher(a, b, on, score_cutoff)

    merged = pd.merge(a, matches, on=on, how=how)
    merged = pd.merge(merged,
                      b.rename(columns={col: col+'_matched' for col in on}),
                      on=[col+'_matched' for col in on],
                      how=how)

    # drop extraneous scores/ other variables

    return merged
