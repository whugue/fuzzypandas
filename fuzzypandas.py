
import time
import pandas as pd
from fuzzywuzzy import fuzz, process


##Quick and dirty function to convert all text to string
def decode_text(text):
    if type(text) == unicode:
        return text.encode("ascii", "replace")
    else:
        return text


##Brute Force Matching (O(N^2) Time)
def brute_force_match(a, b, on, how, cutoff, scorer=fuzz.ratio, show_score):

    ##If multiple key variables, concatenate into single string
    if len(on) > 1:
        a["byvar"] = a[on].apply(lambda x: " ".join(x), axis=1)
        b["byvar"] = b[on].apply(lambda x: " ".join(x), axis=1)
    else:
        a["byvar"] = a[on]
        b["byvar"] = b[on]

    matches = []
    for row in a.byvar.unique():
        match = process.extractOne(row, b.byvar.unique(), scorer=scorer)
        matches.append({"byvar": row, "matched": match[0], "score": match[1]})

    return pd.DataFrame(matches)




def fuzzy_merge(a, b, on, how="left", cutoff=0.6, match_function=brute_force_match, show_score=True):

	##Merge dataframes regularly. Seperate out matches & nonmatches
    a["in_a"] = 1 																	
    b["in_b"] = 1 																	
    
    merged = pd.merge(a, b, on=key, how="outer") 									
    matched = merged[(merged.in_a.notnull()) & (merged.in_b.notnull())].copy()		
    nomatch_a = merged[(merged.in_a.notnull() | (merged.in_b.isnull()))].copy()		
    nomatch_b = merged[(merged.in_a.isnull()) | (merged.in_b.notnull())].copy()		
    
    ##If no non-matches, we're done!. Return matched dataframe
    if nomatch_a.shape[0]==0 | nomatch_b.shape[0]==0:
    	return matched

    ##Otherwise, proceed to fuzzy-matching non-exact matches
	else:
		xwalk = match_function(nomatch_a, nomatch_b, on=on, cutoff=cutoff, show_score=show_score)

		fuzzy_merge1 = pd.merge(nonmatch_a, crosswalk, on=key+"_A", how="left")
    	fuzzy_merge2 = pd.merge(fuzzy_merge1, nonmatch_b, on=key+"_B", how=how) 		

    	return pd.concat([matched, fuzzy_merge_2], axis=0)



