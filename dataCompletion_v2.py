import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
from werkzeug.utils import secure_filename
import pandas as pd
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from urllib.parse import quote
import config
from sqlalchemy.dialects.mysql import LONGTEXT


ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:%s@localhost/datacompletion" % quote(config.sql_password)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/file_uploads'
app.secret_key = config.secret_key

db = SQLAlchemy(app)


class signup(db.Model):
    __tablename__ = 'signup'
    id = db.Column('id',db.Integer, primary_key = True)
    email_id = db.Column(db.String(125))
    name = db.Column(db.String(125))
    password = db.Column(db.String(125))
    usr_id = db.Column(db.String(125))


    def __init__(self, email_id, name, password, usr_id):
        self.email_id = email_id
        self.name = name
        self.password = password
        self.usr_id = usr_id


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def homepage():
    return render_template('index.html')

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False

def is_valid_username(username):
    pattern = r'[^A-Za-z]+'
    print(re.findall(pattern, username))
    if re.findall(pattern, username):
        return False
    else:
        return True


def check_password_strength(password):
    # Check minimum length
    if len(password) < 8:
        msg = "Password must be at least 8 characters long"
        return False, msg
    
    # Check complexity
    if not re.search(r'[A-Z]', password):
        msg = "Password must contain at least one uppercase letter"
        return False, msg
    if not re.search(r'[a-z]', password):
        msg = "Password must contain at least one lowercase letter"
        return False, msg
    if not re.search(r'[0-9]', password):
        msg = "Password must contain at least one digit"
        return False, msg
    if not re.search(r'[@#$%^&+=]', password):
        msg =  "Password must contain at least one special character (@#$%^&+=)"
        return False, msg
    
    # Check exclusions
    if re.search(r'password', password, re.IGNORECASE):
        msg = "Password must not contain the word 'password'"
        return False, msg
    
    # All checks passed
    return True, "Password is strong"

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    '''Check if all required fields are entered if not pop-up not entered condition'''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        psw = request.form['password']
        email = request.form['email']
        UserId = request.form['UserId']
        '''Check whether the email is a valid email or not if not make them enter the valid email'''
        if is_valid_username(username):
            if is_valid_email(email):
                res,msg = check_password_strength(psw)
                if res:
                    flag = 0
                    for i,d in enumerate(db.session.query(signup).all()):
                        dd = d.__dict__
                        if dd['email_id'] == email:
                            msg = 'Account already exists Email Id taken!'
                            flag = 1
                            break
                        if dd['usr_id'] == UserId:
                            msg = "Username is already Taken"
                            flag = 1
                            break
                    if flag == 0:
                        pp = signup(
                            usr_id = UserId,
                            email_id = email,
                            name = username,
                            password = psw
                        )
                        db.session.add(pp)
                        db.session.commit()
                        msg = 'You have successfully registered !'
            else:
                msg = "Please enter a valid email address"
        else:
            msg = "Please enter a valid username. Only support character not interger or special characters"
    elif request.method == 'POST':
        msg = 'Please fill all the required fields from the form !'
    return render_template('register.html', msg=msg)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    flag = 0
    print("Jellp login")
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email_id = request.form['email']
        psw = request.form['password']
        for i,d in enumerate(db.session.query(signup).all()):
            dd = d.__dict__
            if dd['email_id'] == email_id:
                flag = 1
                if dd['password'] == psw:
                    msg = "Logged in successfully!"
                    print(msg)
                else:
                    msg = "Password Incorrect"
                    print(msg)
        if flag == 0:
            msg = "Unable to find the email ID. Please register if not"
            print(msg)


       
    return render_template('login.html', msg=msg)


@app.route("/demo", methods=['GET','POST'])
def demo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = f'static/file_uploads/{filename}'
            if 'csv' in filename:
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath,engine="openpyxl")

            null_values = pd.DataFrame(df.isnull().sum(),columns = ['values'])
            null_values = null_values[null_values['values'] != 0]
            xValues = list(null_values.index)
            yValues = list(null_values['values'])
            piedata = {"xValues":xValues,"yValues":yValues,
                    "barColors":["#b91d47","#00aba9","#2b5797","#e8c3b9","#1e7145"]}

            bardata = {"xValues":["Not Null Values","Null Values"],"yValues":[(df.shape[0]*df.shape[1])-sum(yValues),sum(yValues)],
                    "barColors":["#b91d47","#2b5797"]}

            group_not_null_values = []
            for idx in yValues:
                group_not_null_values.append(len(df) - idx)

            groupedbardata = [
                {
                    "label": 'Not Null Values',
                    "data": group_not_null_values,
                    "borderColor": "#b91d47",
                    "backgroundColor": "#b91d47"
                },
                {
                    "label": 'Null Values',
                    "data": yValues,
                    "borderColor": "#2b5797",
                    "backgroundColor": "#2b5797"
                }]

            data = {"bardata":bardata,"piedata":piedata,'groupedbardata':groupedbardata,'grouplabels':xValues}
            return render_template('eda.html',data = data)
        else:
            flash("Wrong file format!!!")
            return redirect(request.url)
    else:
        return render_template("demo.html")

@app.route('/fillna',methods = ['GET','POST'])
def fillnaValue():
    colours = ['Mean','Median','Mode','None']
    cols = ['ColA','ColB','ColC','ColD']
    if request.method == 'POST':
        fill_methods = []
        for val in request.values.items():
            fill_methods.append(val)
        print("%%"*30)
        print(fill_methods)
    return render_template('fillna.html',colours=colours,cols=cols)

if __name__ == '__main__':
    app.debug = True
    app.run()
    db.create_all()
    app.app_context().push()  