from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'#Mysql@127.0.0.1:3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

@app.route('/')
def homepage():
    import pandas as pd
    import numpy as np


@app.route("/demo", methods=['GET','POST'])
def demo():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        print("**"*20)
        print(f)
        df = pd.read_csv(f.filename)
        msg = f"File uploaded successfully!!! filename is {f.filename}"
        return render_template("demo.html", msg=msg)
    else:
        return render_template("demo.html", msg='')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)

    # data_pure = pd.read_csv('titanic.csv')
    # features_with_nan = [feature for feature in data_pure.columns if data_pure[feature].isnull().sum() >= 1]
    # missing_percentage = []
    # for feature in features_with_nan:
    #     missing_p = {feature: np.round(data_pure[feature].isnull().mean(), 4)}
    #     missing_percentage.append(missing_p)
    #     data_nan = data_pure[features_with_nan]
    #     ##numerical and categorical featires
    #     numerical_features = []
    #     categorical_features = []
    #
    #     for feature in data_nan.columns:
    #         if data_nan[feature].dtype != 'O':
    #             numerical_features.append(feature)
    #         else:
    #             categorical_features.append(feature)
    #
    #             class numerical_feature():
    #                 def mean(data_pure, numerical_features):
    #                     try:
    #                         for i in numerical_features:
    #                             std_before_mean_replacement = np.round(data_pure[i].std(), 4)
    #                             data_pure[i].fillna(data_pure[i].mean(), inplace=True)
    #                             std_After_mean_replacement = np.round(data_pure[i].std(), 4)
    #                             print(
    #                                 "replaced the feature {} with mean and the standard deviation befor applying mean {} and after applying mean is: {}".format(
    #                                     i, std_before_mean_replacement, std_After_mean_replacement))
    #                     except:
    #                         raise Exception
    #
    #                 def median(data_pure, numerical_features):
    #                     try:
    #                         for i in numerical_features:
    #                             std_before_median_replacement = np.round(data_pure[i].std(), 4)
    #                             data_pure[i].fillna(data_pure[i].median(), inplace=True)
    #                             std_After_median_replacement = np.round(data_pure[i].std(), 4)
    #                             print(
    #                                 "replaced the feature {} with median and the standard deviation befor applying median {} and after applying median is: {}".format(
    #                                     i, std_before_median_replacement, std_After_median_replacement))
    #                     except:
    #                         raise Exception
    #
    #                 def mode(data_pure, numerical_features):
    #                     try:
    #                         for i in numerical_features:
    #                             std_before_mode_replacement = np.round(data_pure[i].std(), 4)
    #                             data_pure[i].fillna(data_pure[i].mode()[0], inplace=True)
    #                             std_After_mode_replacement = np.round(data_pure[i].std(), 4)
    #                             print(
    #                                 "replaced the feature {} with mode and the standard deviation befor applying mode {} and after applying mode is: {}".format(
    #                                     i, std_before_mode_replacement, std_After_mode_replacement))
    #                     except:
    #                         raise Exception
    #
    #                 def random_sample(data_pure, numerical_features):
    #                     try:
    #                         for i in numerical_features:
    #                             std_before_random_replacement = np.round(data_pure[i].std(), 4)
    #                             data_pick_random = data_pure[i].dropna().sample(data_pure[i].isnull().sum(),
    #                                                                             random_state=0)
    #                             data_pick_random.index = data_pure[data_pure[i].isnull()].index
    #                             data_pure.loc[data_pure[i].isnull(), i] = data_pick_random
    #                             std_after_random_replacement = np.round(data_pure[i].std(), 4)
    #                             print(
    #                                 "replaced the feature {} with random and the standard deviation befor applying random {} and after applying random is: {}".format(
    #                                     i, std_before_random_replacement, std_after_random_replacement))
    #                     except:
    #                         raise Exception
    #
    #                 def eod_impute(data_pure, numerical_features):
    #                     try:
    #                         for i in numerical_features:
    #                             std_before_eod_replacement = np.round(data_pure[i].std(), 4)
    #                             mean = data_pure[i].mean()
    #                             extreme = mean + 3 * data_pure[i].std()
    #                             data_pure[i].fillna(extreme, inplace=True)
    #                             std_After_eod_replacement = np.round(data_pure[i].std(), 4)
    #                             print(
    #                                 "replaced the feature {} with End of Distribution and the standard deviation befor applying is: {} and after applying is: {}".format(
    #                                     i, std_before_eod_replacement, std_After_eod_replacement))
    #                     except:
    #                         raise Exception

if __name__ == '__main__':
    app.debug = True
    app.run()