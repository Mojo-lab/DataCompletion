import pandas as pd


def main(filepath, col, type):
    if 'csv' in filepath:
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine="openpyxl")

    for c, ty in zip(eval(col), type):
        print(c, ty)
        print("&&"*20)
        print(ty)
        if ty[1].split("__")[0] == "Mean":
            fillV = df[c].mean()
            df[c].fillna(fillV, inplace=True)
            print(f"filled missing value - {c}")
        if ty[1].split("__")[0] == "Mode":
            print(df[c].mode().loc[0])
            fillV = df[c].mode()
            df[c].fillna(fillV[0], inplace=True)
            print(f"filled missing value - {c}")
        if ty[1].split("__")[0] == "Median":
            fillV = df[c].median()
            df[c].fillna(fillV, inplace=True)
            print(f"filled missing value - {c}")
    return df
