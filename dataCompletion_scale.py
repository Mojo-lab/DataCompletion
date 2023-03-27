import pandas as pd
from sklearn.preprocessing import StandardScaler,normalize,MinMaxScaler,MaxAbsScaler,RobustScaler
import numpy as np

def standard_scaler(df,col):
    scaler = StandardScaler()
    data = np.array(df[col]).reshape(-1,1)
    scaler.fit(data)
    data = scaler.transform(data)
    df[col] = data
    return df

def normalizer(df,col):
    data = np.array(df[col]).reshape(-1,1)
    norm = normalize(data)
    df[col] = norm
    return df

def minmax_scale(df,col):
    minmax = MinMaxScaler()
    data = np.array(df[col]).reshape(-1,1)
    minmax.fit(data)
    data = minmax.transform(data)
    df[col] = data
    return df

def max_abs_Scaler(df,col):
    maxabs = MaxAbsScaler()
    data = np.array(df[col]).reshape(-1,1)
    maxabs.fit(data)
    data = maxabs.transform(data)
    df[col] = data
    return df


def robust_scaler(df,col):
    rob_sc = RobustScaler()
    data = np.array(df[col]).reshape(-1,1)
    rob_sc.fit(data)
    data = rob_sc.transform(data)
    df[col] = data
    return df


def col_transformer(df,col_scale):
    for idx in col_scale:
        if idx[1] == "Standardization":
            df = standard_scaler(df,idx[0])
        elif idx[1] == "Normalization":
            df = normalizer(df, idx[0])
        elif idx[1] == "Min-Max Scaling":
            df = minmax_scale(df, idx[0])
        elif idx[1] == "Absolute Maximum Scaling":
            df = max_abs_Scaler(df, idx[0])
        elif idx[1] == "Robust Scaling":
            df = robust_scaler(df, idx[0])
        else:
            pass
    return df

