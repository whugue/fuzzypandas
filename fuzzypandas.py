"""
FuzzyPandas: Approximate String Matching for Pandas Dataframe Joins
"""

import numpy as np
import pandas as pd
import difflib

"""
Define Functions to Map key in dataframe A to key in dataframe B, using various pre-processing steps
a = Pandas Dataframe A
b = Pandas Dataframe B
key = key column (as a string)
cutoff = Fuzzy Match Score Cutoff, 0.0 - 1.0 (0.6 by default)
"""

def ratio_match(a, b, key, cutoff):
	a.rename(columns = {key : key+"_A"}, inplace = True)
	b.rename(columns = {key : key+"_B"}, inplace = True)
	a[key+"_B"] = a[key+"_A"].map(lambda x: difflib.get_close_matches(x, b[key+"_B"], n=1, cutoff=cutoff)[0])

	return a[[key+"_A", key+"_B"]]


def sorted_ratio_match(a, b, key, cutoff):
	a.rename(columns = {key : key+"_A"}, inplace = Truexs)
	b.rename(columns = {key : key+"_B"}, inplace = True)

	a[key+"A_sorted"] = a[key+"_A"].map(lambda x: x.split().sort())
	b[key+"B_sorted"] = b[ley+"_B"].map(lambda x: x.split().sort())

	a[key+"B_sorted"] = a[key+"A_sorted"].map(lambda x: difflib.get_close_matches(x, b[key+"_sorted"], n=1, cutoff=cutoff)[0])

	return pd.merge([a, b], how="left", on=key+"_sorted")[[key+"_A", key+"_B"]]


def set_ratio_match(a, b, key, cutoff):
	pass


def partial_ratio_match(a, b, key, cutoff):
	pass


def partial_sort_ratio_match(a, b, key, cutoff):
	pass


def partial_set_ratio_match(a, b, key, cutoff):
	pass


"""
This is the actual function to use
a = Pandas Dataframe A
b = Pandas Dataframe B
key = Key column (as a string)
cutoff = Fuzzy Match Score Cutoff 0.0 - 1.0 (Defualt = 0.6)
Ratio = Fuzzy Match Ratio Calculation: ["ratio", "sort_ratio", "set_ratio", "partial_ratio", "partial_sort_ratio", "partial_set_ratio", "weighted_ratio]
"""
def fuzzy_merge(a, b, byvar, key, cutoff=0.6, how="left", ratio="ratio"):
    a["in_a"] = 1 																	#Flag rows existing in DF A
    b["in_b"] = 1 																	#Flag rows existing in DF B
    
    merged = pd.merge(a, b, on=key, how="outer") 									#Perform regular Join

    matched = merged[(merged.in_a.notnull()) & (merged.in_b.notnull())].copy()		#Sift out exact matches  
    nomatch_a = merged[(merged.in_a.notnull() | (merged.in_b.isnull()))].copy()		#Sift out nonmatches from DF A
    nomatch_b = merged[(merged.in_a.isnull()) | (merged.in_b.notnull())].copy()		#Sift out nomathches from DF B
    
    if nomatch_a.shape[0]==0 | nomatch_b.shape[0]==0: 								#If no nonmatches in A or B, return matches & end
    	return matched

    else:																			#Otherwise, proceed to fuzzy matching. Create crosswalk key file
    	if ratio == "ratio":
        	crosswalk = ratio_match(nonmatch_a, nonmatch_b, key=key, cutoff=cutoff)

    	elif ratio == "sort_ratio":
    		crosswalk = sort_ratio_match(nonmatch_a, nonmatch_b, key=key, cutoff=cutoff)

    	elif ratio == "set_ratio":
    		crosswalk = set_ratio_match(nonmatch_a, nonmatch_b, key=key, cutoff=cutoff)

    	elif ratio == "partial_ratio":
    		crosswalk = partial_ratio_match(nonmatch_a, nonmatch_b, key=key, cutoff=cutoff)

    	elif ratio == "partial_sort_ratio":
    		crosswalk = partial_sort_ratio_match(nonmatch_a, nonmatch_b, key=key, cutoff=cutoff)

    	elif ratio == "partial_set_ratio":
    		crosswalk = partial_set_ratio(nonmatch_a, nonmatch_b, key=key, cutoff=cutoff)

    	fuzzy_merge1 = pd.merge(nonmatch_a, crosswalk, on=key+"_A", how="left") 		#Match DF A to crosswalk on Key A
    	fuzzy_merge2 = pd.merge(fuzzy_merge1, nonmatch_b, on=key+"_B", how=how) 		#Match DF A+Xwalk to DF B on Key B

    	return pd.concat([matched, fuzzy_merge_2], axis=0) 								#Append fuzzy matches to exact matches and return (MAKE DROPS)

