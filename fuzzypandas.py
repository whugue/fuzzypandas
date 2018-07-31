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


def score_value_pairs(data, match_data, scorer=fuzz.ratio):

    pairs  = []
    score_cache = {}

    for row in data:
        for match_row in match_data:
            pair = {}
            on = convert_to_list(on)

                for key in keys:
                    pair_string = '_'.join(sorted(row[key], match_row[key]))

                    if pair_string in score_cache:
                        score = score_cache[pair_string]

                    else:
                        score = scorer(row[key], match_row[key])
                        score_cache[pair_string] = score

                    pair[col] = pair[col]
                    pair['{col}_matched'.format(col=col)] = pair['col']
                    pair['{col}_match_score'] = score

            pairs.append(pair)

    return pairs


def fuzzy_merge(a, b, keys, scorer=fuzz.ratio, score_cutoff=60):
    '''
    Data and Match data are list of dicts
    '''
    matches = score_value_pairs(a.to_dict('records'), b.to_dict('records'))
    matches = pd.DataFrame(matches)

    cols = matches.columns.tolist()
    score_cols = [col for col in cols where '_match_score' in col]
    other_cols = cols - score_cols

    matches['match_score'] = matches[score_cols].mean(axis=1)
    matches.sort_values(by=matches.columns.tolist(), acending=False, inplace=True)
    matches.drop_duplicates(other_cols, inplace=True)
    matches = matches[matches.match_score <= score_cutoff].copy()

    # TODO -- Merge back onto df
    # need to incorporate the how feature

    return df
    