import pandas as pd


def main(filepath, col, type):
    if 'csv' in filepath:
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine="openpyxl")

    for c, ty in zip(eval(col), type):
        try:
            print("&&" * 20)
            print(ty)
            meth = ty[1].split('___')
            colname = ty[1].split("__")
            print(c)
            print(meth)
            print(colname)
            c = colname[0]
            meth = meth[1]
            if meth == "Mean":
                fillV = df[c].mean()
                df[c].fillna(fillV, inplace=True)
                print(f"filled missing value - {c}")
            if meth == "Mode":
                print(df[c].mode().loc[0])
                fillV = df[c].mode()
                df[c].fillna(fillV[0], inplace=True)
                print(f"filled missing value - {c}")
            if meth == "Median":
                fillV = df[c].median()
                df[c].fillna(fillV, inplace=True)
                print(f"filled missing value - {c}")
        except IndexError:
            pass
    return df
