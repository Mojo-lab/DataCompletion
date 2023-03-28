import pandas as pd
from sklearn.preprocessing import LabelEncoder


def label_encode_data(df,col):
    le = LabelEncoder()
    le.fit(df[col])
    new_col = f"{col}_categorical"
    df[new_col] = le.transform(df[col])
    class_names = le.classes_
    return df,class_names

def nominal_encoding(df,col):
    nominal_features = df[col]
    nominal_features = pd.get_dummies(nominal_features, drop_first=True)
    nominal_features = pd.concat([df,nominal_features],axis=1)
    return nominal_features


def encode_catdata(df, col_scale):
    for idx in col_scale:
        if idx[1] == "Label Encoding":
            df = label_encode_data(df,idx[0])[0]
        elif idx[1] == "Nominal Encoding":
            df = nominal_encoding(df,idx[0])
        else:
            pass
    return df


# df = pd.read_excel(r'C:\Users\Home\Desktop\CollectionMonitoringReport20220121101935.xlsx')
# print(df)
# z = label_encode_data(df,'Status')
#
# z1 = z[0]
# print(z)
