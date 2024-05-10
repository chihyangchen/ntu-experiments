import datetime as dt
import numpy as np
import re
from .signal_strength import SS
from .pkg_loss_excl import PKG


def find_longest_common_substring_length(str1, str2):
    len1 = len(str1)
    len2 = len(str2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    max_length = 0  
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                max_length = max(max_length, dp[i][j])

    return max_length

def add_nan(Cell, add=dt.timedelta(seconds=1)):
    
    L = []
    for i in range(len(Cell)-1):
        dif = (Cell[i+1].Timestamp - Cell[i].Timestamp).total_seconds()
        L.append(Cell[i])
        if dif > 1:
            L.append(SS('', '', np.nan, np.nan, Cell[i].Timestamp+add))

    return L

def add_nan_pkg(pkgs, add=dt.timedelta(seconds=0.1)):
    
    L = []
    for i in range(len(pkgs)-1):
        dif = (pkgs[i+1].Timestamp - pkgs[i].Timestamp).total_seconds()
        L.append(pkgs[i])
        if dif > 0.2:
            L.append(PKG(pkgs[i].Timestamp+add,0,np.nan))

    return L

# Useful Functions
def get_info(ordered_HOs, time_range=None):

    T, Type, Trans, Ev = [], [], [], []
    for element in ordered_HOs:
        NO_MR = False
        try:
            type, ho, mr = element[0], element[1], element[2]
        except:
            type, ho = element[0], element[1]
            NO_MR = True

        if time_range is not None and ho.start < time_range[0]:
            continue
        elif time_range is not None and time_range[1] < ho.start:
            break
        else: # in time range
            type = type.replace("_", " ")
            
            T.append(ho.start)
            Type.append(type)
            Trans.append(ho.trans)
            if NO_MR:
                Ev.append(None)
            else:
                Ev.append(mr.event)
    
    return T, Type, Trans, Ev

patterns = {
    'eNB HO': r'\((\d+), (\d+)\) -> \((\d+), (\d+)\)',
    'gNB HO': r'(\d+) -> (\d+)',
    'gNB setup': r'O -> (\d+)',
    'gNB rel':r'\((\d+), (\d+)\) \| (\d+) -> O' 
    }
def get_pci(string, type):
    pattern = patterns[type]
    match = re.match(pattern, string)

    if match:
        if type == 'eNB HO':
            return f'{match.group(1)}\u2192{match.group(3)}'
        elif type == 'gNB HO':
            return f'{match.group(1)}\u2192{match.group(2)}'
        elif type == 'gNB setup':
            return f'{match.group(1)}'
        elif type == 'gNB rel':
            return f'{match.group(3)}\u2192N/A'
    else:
        if type == 'gNB HO':
            pattern = r'O -> (\d+)'
            match = re.match(pattern, string)
            return f'O\u2192{match.group(1)}'

    return None