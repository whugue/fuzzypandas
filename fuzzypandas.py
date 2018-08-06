import pandas as pd
from scorer import Scorer


def fuzzy_merge(a, b, on, how='left', scoring='weighted ratio', score_cutoff=60, processes=None):
  '''
  Impliment a Fuzzy Merge
  '''
  # make sure on is a list 
  on = utils.convert_to_list(on)

  # impliment scoring
  methods = {'weighted ratio': fuzz.Wratio,
             'ratio': fuzz.ratio,
             'partial ratio': fuzz.partial_ratio,
             'token sort ratio': fuzz.token_sort_ratio,
             'token set ratio': fuzz.token_set_ratio,
             'partial token set ratio': fuzz.partial_token_set_ratio}

  scorer = Scorer()
  matches = scorer.score(data1=a.to_dict('records'),
                         data2=b.to_dict('records'),
                         keys=on,
                         method=methods[scoring],
                         processes=processes)

  # get best matches from scoring results
  matches = pd.DataFrame(matches)

  matches.sort_values(by=on + ['avg_match_score'],
                      ascending=[True] * len(on) + [False],
                      inplace=True)
  matches.drop_duplicates(on, inplace=True)

  # only keep matches above score_cutoff threshold
  matches = matches[matches.match_score >= score_cutoff].copy()

  # use best matches to merge dataframes A and B
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
