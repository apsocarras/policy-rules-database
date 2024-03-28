import os
import datetime as dt 
import matplotlib.pyplot as plt 
import json
import yaml
import pandas as pd 
import numpy as np
from scipy.signal import argrelextrema

### ------------------------------------------------------------------------------ ###
### --- GENERAL UTILS  --- ###

def print_df(df):
    for line in df.to_csv(index=False).splitlines(): 
        print(line.replace(',',', '))

def combine_dicts(*dicts):
    combined_dict = {}
    for d in dicts:
        combined_dict.update(d)
    return combined_dict

def get_hourly_wage(annual):
    # Assuming you work a 40 hour week, 52 weeks in a year 
    return f"${(annual/52)/40:.2f}"

def format_int_dollars(n:int) -> str: 
    return '${:,.6}'.format(float(n)).rstrip('0').rstrip('.')


def find_derivative_rel_minima(x,y, non_negative=True): 
    """Find rel minima (indices) of a derivative """
    ## Derivative  
    derivative = np.gradient(y,x)
    derivative_rel_minima = argrelextrema(derivative, np.less)[0]
    if non_negative:
        derivative_rel_minima = derivative_rel_minima[derivative_rel_minima > 0] # non-negative
    return derivative_rel_minima

def find_zero_intercepts(ls:list):
    """Get points (indices) of curve (iterable) which first intersect with x-axis (0) (i.e. previous value must be non-zero)""" 

    zero_indices = []
    on_zero = True  # treat first element in list as if we're already on zero (there's no previous point)
    for n in range(len(ls)):
        if ls[n] == 0:
            if not on_zero: # i.e. we found a zero and we're not already on the axis 
                zero_indices.append(n)
                on_zero = True
            else: 
                continue
        else: 
            on_zero = False

    return zero_indices

### ------------------------------------------------------------------------------ ###
### --- BENEFITS FUNCTIONS --- ###

def filter_benefits(df, include_eitc=True): 
    """Filter df to relevant benefits columns"""
    df_benefits = df.loc[:, ((df != 0).any(axis=0) & (df == 0).any(axis=0))]\
            .filter(regex='value') # Must have non-zero and zero values to potentially cause a cliff
    if not include_eitc: 
        df_benefits = df_benefits[[col for col in df_benefits.columns if 'eitc' not in col]]
    return df_benefits


def find_benefits_cliffs(df, derivative_rel_minima, mode='peak') -> dict: 
    """Find benefits cliffs from zeros in benefits curves and the minima of the derivative of the income vs. net resources curve
    
    Args

    df (dataframe): Dataframe with benefits columns recognized in filter_benefits()

    mode (str): 'peak' (return index of peak of cliff) or 'valley' (return index of bottom of cliff)
    
    Returns 

    cliffs (dict): {<benefits_column>:[<cliff-1>,...,<cliff-n>]}
    
    """

    if mode == 'peak': 
        offset = 1
    elif mode == 'valley': 
        offset = 0
    else: 
        raise Exception("'mode' must be one of 'peak' or 'valley'")
 
    df_benefits = filter_benefits(df, include_eitc=False)
    cliffs = {}

    for col in df_benefits.columns: 
        zeros = find_zero_intercepts(df_benefits[col].tolist())
        col_cliffs = [x - offset for x in zeros if any(x in range(e,e+2) for e in derivative_rel_minima)] # pd.Interval(e-1,e+1, closed='both') -- since derivative curve is discrete I don't think this is need
        if len(col_cliffs) > 0:
            cliffs[col] = col_cliffs

    return cliffs 


### ------------------------------------------------------------------------------ ###
## --- DEPRECATED: Used for illustration in identify-cliffs-plotly.ipynb only ---  ##

def find_zeros(df,include_first=False) -> list: 
    """Find the first index of zero in each column of a dataframe"""
    if include_first: 
        zeros = [{col:df[col].to_list().index(0)} for col in df.columns]
    else: 
        zeros = []
        for col in df.columns: 
            idx_first_nonzero = -1
            for n,v in enumerate(df[col].values): 
                if v > 0:
                    idx_first_nonzero = n
                    break      
            try: 
                zero = df[col][idx_first_nonzero:].to_list().index(0)
            except ValueError: 
                continue # no zero in rest of the column
            if zero != -1: 
                zeros.append({col:zero})
    zeros.sort(key=lambda x: list(x.values())[0])
    return zeros 


# def find_benefits_cliffs(zeros, derivative_rel_minima) -> list: 
#     """Find benefits cliffs points from zeros in benefits curves and the derivative minima"""

#     cliffs = [{"benefit":list(z.keys())[0],
#                 "valley":list(z.values())[0], 
#                 "peak":list(z.values())[0] - 1}
#             for z in zeros 
#             if any(list(z.values())[0] in pd.Interval(e-1,e+1, closed='both')
#                 for e in derivative_rel_minima)]
    
#     return cliffs 



## --- DEPRECATED: Prior version of repo before I created the BeneficiaryProfile Class ---  ##

def print_ben_sum(ben_dict:dict, indent=4):
    ## Print summarized version of the profile for confirmation  
    print(json.dumps({
        x:y for x,y in ben_dict.items() 
            if y != ['NA'] and not (any(str(n) in x for n in range(2,13)) and y == [0])
    }, indent=indent))
        
    
def create_ben_profile_dict(**kwargs) -> dict: 
    """Creates a ben profile using the default yaml template as a base.
    Add keyword arguments to change specific values in the default (recommend a dictionary format).
    Will print summary version of the dictionary for reference."""

    ## Set Default from provided TEST 
    def_ben_profile = {
        'ruleYear': [2023],
        'Year': [2023], # I have not noticed this change anything
        'agePerson1': [30],
        'agePerson2': [8],
        'agePerson3': ['NA'],
        'agePerson4': ['NA'],
        'agePerson5': ['NA'],
        'agePerson6': ['NA'],
        'agePerson7': ['NA'],
        'agePerson8': ['NA'],
        'agePerson9': ['NA'],
        'agePerson10': ['NA'],
        'agePerson11': ['NA'],
        'agePerson12': ['NA'],
        'married': [0],
        'disability1': [0],
        'disability2': [0],
        'disability3': [0],
        'disability4': [0],
        'disability5': [0],
        'disability6': [0],
        'disability7': [0],
        'disability8': [0],
        'disability9': [0],
        'disability10': [0],
        'disability11': [0],
        'disability12': [0],
        'prev_ssi': [0],
        'blind1': [0],
        'blind2': [0],
        'blind3': [0],
        'blind4': [0],
        'blind5': [0],
        'blind6': [0],
        'ssdiPIA1': [0],
        'ssdiPIA2': [0],
        'ssdiPIA3': [0],
        'ssdiPIA4': [0],
        'ssdiPIA5': [0],
        'ssdiPIA6': [0],
        'locations': ['all'],
        'income_start': 1000,
        'income_end': 100000,
        'income_increase_by': 30000,
        'income.investment': [0],
        'income.gift': [0],
        'income.child_support': [0],
        'empl_healthcare': [0],
        'ownorrent': ['rent'],
        'assets.cash': [0],
        'assets.car1': [0],
        'disab.work.exp': [0],
        'k_ftorpt': 'FT',
        'schoolagesummercare': 'PT',
        'headstart_ftorpt': 'PT',
        'preK_ftorpt': 'PT',
        'contelig.headstart': False,
        'contelig.earlyheadstart': False,
        'contelig.ccdf': True,
        'budget.ALICE': 'survivalforcliff',
        'APPLY_CHILDCARE': True,
        'APPLY_HEADSTART': True,
        'APPLY_CCDF': True,
        'APPLY_PREK': True,
        'APPLY_LIHEAP': False,
        'APPLY_HEALTHCARE': True,
        'APPLY_MEDICAID_ADULT': True,
        'APPLY_MEDICAID_CHILD': True,
        'APPLY_ACA': True,
        'APPLY_SECTION8': True,
        'APPLY_RAP': False,
        'APPLY_FRSP': False,
        'APPLY_SNAP': True,
        'APPLY_SLP': True,
        'APPLY_WIC': True,
        'APPLY_EITC': True,
        'APPLY_TAXES': True,
        'APPLY_CTC': True,
        'APPLY_CDCTC': True,
        'APPLY_FATES': False,
        'APPLY_TANF': True,
        'APPLY_SSI': True,
        'APPLY_SSDI': True
    }
    
    ## Make adjustments from kwargs 
    new_ben_profile = def_ben_profile.copy()
    for k,v in kwargs.items(): 
        ## TO-DO: write complete validation function for all key:value parameters 
        if k not in def_ben_profile.keys():
            raise ValueError(f'{k} not a valid key in beneficiary configuration schema')
        else: 
            new_ben_profile[k] = v

    return new_ben_profile

def print_ben_sum(ben_dict:dict, indent=4):
    ## Print summarized version of the profile for confirmation  
    print(json.dumps({
        x:y for x,y in ben_dict.items() 
            if y != ['NA'] and not (any(str(n) in x for n in range(2,13)) and y == [0])
    }, indent=indent))
    

def save_config(ben_profile_dict:dict, project_name:str): 
    """Save to a yaml file and run the R script"""
    ## TO-DO: Use validation schema function to check ben profile 

    ## Save to yaml
    with open(os.path.join('projects', project_name + '.yaml'), 'w') as file: 
        yaml.dump(ben_profile_dict, file, indent=4) # note that unlike the default example file, 
        # the key-value pairs will be in alphabetical order and the file will be missing the comments
    
    print(f'Saved to {os.path.join("projects", project_name + ".yaml")}')
    print(f'Project name: {project_name}')

def read_output(project_name:str) -> pd.DataFrame:
    """Read output of R script based on project (YAML config) name"""
    return pd.read_csv(os.path.join('output', f'results_{project_name}.csv'))


