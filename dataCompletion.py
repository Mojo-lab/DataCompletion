from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def homepage():
    import pandas as pd
    data_pure = pd.read_csv('titanic.csv')
    features_with_nan = [feature for feature in data_pure.columns if data_pure[feature].isnull().sum() >= 1]
    missing_percentage = []
    for feature in features_with_nan:
        missing_p = {feature: np.round(data_pure[feature].isnull().mean(), 4)}
        missing_percentage.append(missing_p)
        data_nan = data_pure[features_with_nan]
        ##numerical and categorical featires
        numerical_features = []
        categorical_features = []

        for feature in data_nan.columns:
            if data_nan[feature].dtype != 'O':
                numerical_features.append(feature)
            else:
                categorical_features.append(feature)


if __name__ == '__main__':
    app.debug = True
    app.run()