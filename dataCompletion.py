from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def homepage():
    import pandas as pd
    import numpy as np

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

                class numerical_feature():
                    def mean(data_pure, numerical_features):
                        try:
                            for i in numerical_features:
                                std_before_mean_replacement = np.round(data_pure[i].std(), 4)
                                data_pure[i].fillna(data_pure[i].mean(), inplace=True)
                                std_After_mean_replacement = np.round(data_pure[i].std(), 4)
                                print(
                                    "replaced the feature {} with mean and the standard deviation befor applying mean {} and after applying mean is: {}".format(
                                        i, std_before_mean_replacement, std_After_mean_replacement))
                        except:
                            raise Exception

                    def median(data_pure, numerical_features):
                        try:
                            for i in numerical_features:
                                std_before_median_replacement = np.round(data_pure[i].std(), 4)
                                data_pure[i].fillna(data_pure[i].median(), inplace=True)
                                std_After_median_replacement = np.round(data_pure[i].std(), 4)
                                print(
                                    "replaced the feature {} with median and the standard deviation befor applying median {} and after applying median is: {}".format(
                                        i, std_before_median_replacement, std_After_median_replacement))
                        except:
                            raise Exception

                    def mode(data_pure, numerical_features):
                        try:
                            for i in numerical_features:
                                std_before_mode_replacement = np.round(data_pure[i].std(), 4)
                                data_pure[i].fillna(data_pure[i].mode()[0], inplace=True)
                                std_After_mode_replacement = np.round(data_pure[i].std(), 4)
                                print(
                                    "replaced the feature {} with mode and the standard deviation befor applying mode {} and after applying mode is: {}".format(
                                        i, std_before_mode_replacement, std_After_mode_replacement))
                        except:
                            raise Exception

                    def random_sample(data_pure, numerical_features):
                        try:
                            for i in numerical_features:
                                std_before_random_replacement = np.round(data_pure[i].std(), 4)
                                data_pick_random = data_pure[i].dropna().sample(data_pure[i].isnull().sum(),
                                                                                random_state=0)
                                data_pick_random.index = data_pure[data_pure[i].isnull()].index
                                data_pure.loc[data_pure[i].isnull(), i] = data_pick_random
                                std_after_random_replacement = np.round(data_pure[i].std(), 4)
                                print(
                                    "replaced the feature {} with random and the standard deviation befor applying random {} and after applying random is: {}".format(
                                        i, std_before_random_replacement, std_after_random_replacement))
                        except:
                            raise Exception

                    def eod_impute(data_pure, numerical_features):
                        try:
                            for i in numerical_features:
                                std_before_eod_replacement = np.round(data_pure[i].std(), 4)
                                mean = data_pure[i].mean()
                                extreme = mean + 3 * data_pure[i].std()
                                data_pure[i].fillna(extreme, inplace=True)
                                std_After_eod_replacement = np.round(data_pure[i].std(), 4)
                                print(
                                    "replaced the feature {} with End of Distribution and the standard deviation befor applying is: {} and after applying is: {}".format(
                                        i, std_before_eod_replacement, std_After_eod_replacement))
                        except:
                            raise Exception

if __name__ == '__main__':
    app.debug = True
    app.run()