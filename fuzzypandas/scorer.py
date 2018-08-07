import warnings
from fuzzywuzzy import fuzz
from fuzzypandas import utils
from multiprocessing import Pool

class Scorer:

    def __init__(self):
        self.score_cache = {}  # not sure if this is right way to do caching...

    def score_pair(self, row, keys, method):
        '''
        Score a pair of values based on given scoring function
        '''
        result = {}
        sum_scores = 0

        for i, key in enumerate(keys, start=1):

            value1 = utils.convert_to_string(row[0][key])
            value2 = utils.convert_to_string(row[1][key])

            value_pair = tuple(sorted([value1, value2]))

            if value_pair in self.score_cache:
                score = self.score_cache[value_pair]
            else:
                score = method(value1, value2)
                self.score_cache[value_pair]

            sum_scores += score
            avg_score = sum_scores / i

            result['{col}_A'.format(col=key)] = value1
            result['{col}_B'.format(col=key)] = value2
            result['{col}_match_score'.format(col=key)] = score

        result['match_score'] = avg_score

        return result

    def score(self, data1, data2, keys, scoring, processes):

        # create cartesian product of data
        data = utils.cartesian_product(data1, data2)

        # define scoring method
        methods = {'weighted ratio': fuzz.Wratio,
                   'ratio': fuzz.ratio,
                   'partial ratio': fuzz.partial_ratio,
                   'token sort ratio': fuzz.token_sort_ratio,
                   'token set ratio': fuzz.token_set_ratio,
                   'partial token set ratio': fuzz.partial_token_set_ratio}

        if scoring not in methods:
            warnings.warn('{scoring} not a valid scoring method. Using "Weighted Ratio."'.format(scoring=scoring))
            method = fuzz.WRatio

        else:
            method = method[scoring]

        # score all pairs via multiprocessing
        if processes:
            if processes > 1:
                pool = Pool(processes)
                results = [pool.apply(self.score_pair, args=(row, keys, method)) for row in data]

            else:
                results = [self.score_pair(row, keys, method) for row in data]

        else:
            results = [self.score_pair(row, keys, method) for row in data]

        return results
