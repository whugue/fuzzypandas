

import pyprind
import pandas as pd
from fuzzywuzzy import fuzz, process


"""
Basic Match Function 
"""

def basic_match(a, b, keyA, keyB, cutoff, quickmatch):

    title = "Fuzzy Matching Results"
    #bar = pyprind.ProgBar(50, monitor=True, title=title)

    matches = []
    for row in a[keyA].unique():

        if quickmatch==True:
            match = process.extractOne(row, b[keyB].unique(), scorer=fuzz.ratio, score_cutoff=cutoff)
        else:
            match = process.extractOne(row, b[keyB].unique(), scorer=fuzz.WRatio, score_cutoff=cutoff)

        if match == None:
            matches.append({"keyA": row, "keyB": None, "match_score": None})
        else:
            matches.append({"keyA": row, "keyB": match[0], "match_score": match[1]})

        #bar.update()

    #print bar
    return pd.DataFrame(matches)

"""
Hierarchical Match Function
"""

def hier_match(a, b, cutoff, quickmatch):
    pass


"""
Dataframe Merge Function
"""

def fuzzy_merge(a, b, on, how="left", matcher=basic_match, cutoff=60, quickmatch=True):

	##Perform exact match on dataframes A and B
    a["in_a"] = 1 																	
    b["in_b"] = 1

    merged = pd.merge(a, b, on=on, how="outer")


    ##Split results into matches & nonmatches 
    matched = merged[(merged.in_a.notnull()) & (merged.in_b.notnull())].copy()
    nomatch_a = merged[(merged.in_a.notnull() & (merged.in_b.isnull()))].copy()		
    nomatch_b = merged[(merged.in_a.isnull()) & (merged.in_b.notnull())].copy()

    matched["match_score"] = 100 ##All Exact matches get a match score of 100% by default


    ##If no non-matches, we're done!. Return matched dataframe
    if min(nomatch_a.shape[0], nomatch_b.shape[0])==0:
        return matched

    ##Otherwise, try to fuzzy match the nonmatches and append any new matches
    else:
        if type(on) == list:
            nomatch_a["keyA"] = a[on].apply(lambda x: " ".join(x), axis=1)
            nomatch_b["keyB"] = b[on].apply(lambda x: " ".join(x), axis=1)
        else:
            nomatch_a["keyA"] = a[on]
            nomatch_b["keyB"] = b[on]

        xwalk = matcher(nomatch_a, nomatch_b, keyA="keyA", keyB="keyB", cutoff=cutoff, quickmatch=quickmatch)

        fuzzy_merge1 = pd.merge(nomatch_a, xwalk, on="keyA", how="left")
        fuzzy_merge2 = pd.merge(fuzzymerge1, nomatch_b, on="keyB", how=how)

        return fuzzy_merge2
        #return pd.concat([matched, fuzzy_merge2], axis=0)









