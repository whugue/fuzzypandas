import sys
import utils
import logging
import pandas as pd
from fuzzywuzzy import fuzz


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def score_pairs(data, match_data, keys, scorer):
    '''
    For each row in "data" and row in "match_data",
    compute the string similarity of the key fields and save the average score
    '''
    combos = len(data) * len(match_data) * len(keys)
    logger.info('Starting Pair Scoring for {n} combinations.'.format(n=combos))

    # Set up containers for data and score cache
    pairs = []
    score_cache = {}

    # Iterate through each row in the first dataset
    for row in data:

        # Iterate through each row in the second dataset
        for match_row in match_data:

            # Create a container to hold the fuzzy matching scores for that row
            pair = {}
            sum_scores = 0

            # Iterate through each variable we are matching on
            for i, key in enumerate(keys, start=1):

                value = utils.convert_to_string(row[key])
                match_value = utils.convert_to_string(match_row[key])

                # If we've alrady scored this pair of values, use the cached score
                # Otherwise, score the pair of strings and add to the cache
                value_pair = tuple(sorted([value, match_value]))

                if value_pair in score_cache:
                    score = score_cache[value_pair]
                else:
                    score = scorer(value, match_value)
                    score_cache[value_pair] = score

                # Compute the average score for all fields scored so far
                sum_scores += score
                avg_score = sum_scores / i

                # Add to the row
                pair['{col}_A'.format(col=key)] = row[key]
                pair['{col}_B'.format(col=key)] = match_row[key]
                pair['{col}_match_score'.format(col=key)] = score  # take this out later, only keep avg match score
                pair['match_score'] = avg_score

            # Add to the data container
            pairs.append(pair)

    logger.info('Completed pair matching.')
    return pairs


def matcher(a, b, on, scorer, score_cutoff):
    '''
    Get best matches
    '''
    # Score "on" columns between dataframes A and B
    pairs = score_pairs(data=a.to_dict('records'),
                        match_data=b.to_dict('records'),
                        keys=on,
                        scorer=scorer)
    # Convert scored data to a dataframe
    pairs = pd.DataFrame(pairs)

    # Select best match for each row.
    pairs.sort_values(by=on + ['avg_match_score'],
                      ascending=[True] * len(on) + [False],
                      inplace=True)
    pairs.drop_duplicates(on, inplace=True)

    # only keep matches above score_cutoff threshold
    pairs = pairs[pairs.avg_match_score >= score_cutoff].copy()

    return pairs


def fuzzy_merge(a, b, on, how='left', scoring='weighted ratio', score_cutoff=60):
    '''
    Fuzzy match dataframe a onto dataframe b
    '''
    # Validate keys ("on")
    on = utils.validate_keys(on)

    matches = matcher(a, b, on, scorer, score_cutoff)

    scoring

    merged = pd.merge(a, matches,
                      left_on=on,
                      right_on=['{col}_A'.format(col=col) for col in on],
                      how=how)

    merged = pd.merge(merged, b.rename(colunns={col: '{col}_matched' for col in on})
                      left_on=['{col}_B'.format(col=col) for col in on],
                      right_on=['{col}_matched'.format(col=col) for col in on],
                      how=how)

    # delete extraneous columns used for fuzzy matching
    for col in on:
        del merged['{col}_A'.format(col=col)]
        del merged['{col}_B'.format(col=col)]
        del merged['{col}_C'.format(col=col)]

    return merged

# TODO:
# Test join types (left, right, inner, outer)
# Test scalability
# Test with unicode values

