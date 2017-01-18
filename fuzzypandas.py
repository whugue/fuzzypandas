

import pyprind
import pandas as pd
from fuzzywuzzy import fuzz, process


"""
Basic Match Function 
"""

def basic_match(keysA, keysB, cutoff, quickmatch):
    #bar = pyprind.ProgBar(50, monitor=True)

    matches = []
    for keyA in keysA:

        if quickmatch==True:
            match = process.extractOne(keyA, keysB, scorer=fuzz.ratio, score_cutoff=cutoff)
        else:
            match = process.extractOne(kayA, keysB, scorer=fuzz.WRatio, score_cutoff=cutoff)

        if match == None:
            matches.append({"keyA": keyA, "keyB": None, "match_score": None})
        else:
            matches.append({"keyA": keyA, "keyB": match[0], "match_score": match[1]})

        #bar.update()

    #print bar
    return pd.DataFrame(matches)

"""
Hierarchical Match Function
"""

def hier_match(keysA, keysB, cutoff, quickmatch):
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

    matched["match_score"] = 100 ##exact matches get a defacto match score of 100%


    ##If no non-matches, we're done!. Return matched dataframe
    if min(nomatch_a.shape[0], nomatch_b.shape[0])==0:
        return matched

    ##Otherwise, use fuzzy matching
    else:
        if type(on) == list:
            nomatch_a["keyA"] = nomatch_a[on].apply(lambda x: " ".join(x), axis=1)
            nomatch_b["keyB"] = nomatch_b[on].apply(lambda x: " ".join(x), axis=1)
        else:
            nomatch_a["keyA"] = nomatch_a[on]
            nomatch_b["keyB"] = nomatch_b[on]

        xwalk = matcher(nomatch_a.keyA.unique(), nomatch_b.keyB.unique(), cutoff=cutoff, quickmatch=quickmatch)

        fuzzy_merge1 = pd.merge(nomatch_a, xwalk, on="keyA", how="left")
        fuzzy_merge2 = pd.merge(fuzzy_merge1, nomatch_b, on="keyB", how=how)

        return fuzzy_merge2
        #return pd.concat([matched, fuzzy_merge2], axis=0) ##debug this, then run on script w/ whole dataset