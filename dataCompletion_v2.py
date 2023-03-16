import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file,jsonify
import re
from werkzeug.utils import secure_filename
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from urllib.parse import quote
import config, dataCompletion_fill
from sqlalchemy.dialects.mysql import LONGTEXT
from flask_mail import Mail, Message
from eda_charts import null_value_graphs,eda_report

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
CORS(app)
mail = Mail()
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:%s@localhost/datacompletion" % quote(config.sql_password)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:%s@localhost/userAccounts" % quote(config.sql_password)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/file_uploads'
app.secret_key = config.secret_key

mail.init_app(app)
logged_in = "False"
username = ''
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

class fileMetadata(db.Model):
    __tablename__ = 'fileMetadata'
    id = db.Column('id',db.Integer, primary_key = True)
    username = db.Column(db.String(125))
    name = db.Column(db.String(125))
    filename = db.Column(db.String(125))


    def __init__(self, username, name, filename):
        self.username = username
        self.name = name
        self.filename = filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        msg = "Password must contain at least one special character (@#$%^&+=)"
        return False, msg

    # Check exclusions
    if re.search(r'password', password, re.IGNORECASE):
        msg = "Password must not contain the word 'password'"
        return False, msg

    # All checks passed
    return True, "Password is strong"


@app.route('/')
def homepage():
    print("--**--"*30)
    print("Home page : ")
    print(f"user logged in - {logged_in}")
    print(f"Current user - {username}")
    print("--**--"*30)
    return render_template('index.html',loggedin=logged_in,usrname=username)


@app.route("/demo", methods=['GET', 'POST'])
def demo():
    print("***---" * 30)
    print(request.method)
    print(request.values)
    print(request.form)
    print(request.url)
    if request.method == 'POST':
        print(request.method)
        # check if the post request has the file part
        print(request.files)
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
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except PermissionError:
                print("File already opened in another software")
            filepath = f'static/file_uploads/{filename}'
            session['folder_path'] = filepath
            data = null_value_graphs(filepath, filename,session)
            print(request.endpoint)
            return render_template('eda.html', data=data, loggedin=logged_in,usrname=username)
        else:
            flash("Wrong file format!!!")
            return redirect(request.url)
    else:
        return render_template("demo.html", loggedin=logged_in,usrname=username)


@app.route('/eda/<string:fname>', methods=['GET'])
def eda(fname):
    print("88" * 20)
    print(request.method)
    print(request.endpoint)
    filename = fname
    filepath = f'static/file_uploads/{filename}'
    session['folder_path'] = filepath
    data = null_value_graphs(filepath, filename,session)
    return render_template("eda.html", data=data, usrname=username, loggedin=logged_in)

@app.route('/edareport',methods=['GET'])
def edareport():
    filepath = session.get("folder_path")
    data = eda_report(filepath)
    return render_template('edareport.html',data=data[0],data1=data[1],data2=data[2], loggedin=logged_in,usrname=username)

@app.route('/newwork', methods=['GET', 'POST'])
def newwork():
    if request.method == 'POST':
        print("***---" * 30)
        print(request.method)
        print(request.values)
        print(request.form)
        print(request.url)
        print("sub")
        print(request.files)
        name = request.form['fname']
        file = request.files['file']

        print("i'm here!!")
        print(name)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            paths = os.path.join(os.getcwd(), "static", "file_uploads", "user_raw_data", username)

            try:
                os.mkdir(paths)
            except FileExistsError:
                pass

            filepath = os.path.join(paths, filename)
            file.save(filepath)

        pp = fileMetadata(
            username=username,
            name=name,
            filename=filename
        )
        db.session.add(pp)
        db.session.commit()

        session['folder_path'] = filepath
        data = null_value_graphs(filepath, filename,session)
        return render_template('eda.html', data=data, usrname=username, loggedin=logged_in)
    else:
        return render_template('newwork.html', loggedin=logged_in,usrname=username)


@app.route('/fillna', methods=['GET', 'POST'])
def fillnaValue():
    colours = ['Mean', 'Median', 'Mode', 'None']
    fillmeth = ['Categorical', 'Continuous']
    col = session.get("Column_names")
    print(col)
    folder_path = session.get('folder_path')
    cols = eval(col)
    download_file_status = ""
    downloadlink = ''
    downloadmessage = ''
    if request.method == 'POST':
        fill_methods = []
        print(request.values)
        folder_path = session.get('folder_path')
        col = session.get("Column_names")
        for val in request.values.items():
            fill_methods.append(val)
        df = dataCompletion_fill.main(folder_path, col, fill_methods)
        print(df.isnull().sum())
        df.to_csv(folder_path, index=False)
        download_file_status = "Download File"
        downloadlink = '/getdata'
        downloadmessage = 'EasyFill has finished filling the missing values!'
    else:
        print("Method GET")
        # print(df.isnull().sum())
    return render_template('fillna.html', colours=colours, cols=cols, filestatus=download_file_status,
                           downloadlink=downloadlink, downloadmessage=downloadmessage, fillmeth=fillmeth,loggedin=logged_in,usrname=username)


@app.route("/getdata")
def getdata():
    folder_path = session.get('folder_path')
    if '.csv' in folder_path:
        file_type = 'text/csv'
    else:
        file_type = "text/xlsx"
    return send_file(
        folder_path,
        mimetype=file_type,
        download_name='EasyFilledData.csv',
        as_attachment=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in, username
    msg = ''
    flag = 0
    print(request.form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email_id = request.form['email']
        psw = request.form['password']
        for i, d in enumerate(db.session.query(signup).all()):
            dd = d.__dict__
            if dd['email_id'] == email_id:
                flag = 1
                if dd['password'] == psw:
                    msg = "Logged in successfully!"
                    print(msg)
                    username = dd['name']
                    logged_in = "True"
                    # user_db = pd.read_excel("static/user_file_db.xlsx",engine="openpyxl")
                    createdFiles = []
                    for i, s in enumerate(db.session.query(fileMetadata).all()):
                        ss = s.__dict__
                        if ss["username"] == username:
                            # for i,path in os.listdir(os.path.join(os.getcwd(),"static","file_uploads","user_imputed_data",username)):
                            createdFiles.append({"file": ss['filename'], "name": ss['name']})

                    # user_db = user_db[user_db['username'] == username]

                    try:
                        createdFiles
                    except UnboundLocalError:
                        createdFiles = []
                    if len(createdFiles) == 0:
                        lenofdata = "No records found..."
                    else:
                        lenofdata = ''
                    return render_template("userHome.html", user=username, createdFiles=createdFiles,
                                           lenofdata=lenofdata,loggedin=logged_in,usrname=username)
                else:
                    msg = "Password Incorrect"
                    print(msg)
            else:
                msg ="Invalid Username or EMAIL"
        if flag == 0:
            msg = "Unable to find the email ID. Please register if not"
            print(msg)

    return render_template('login.html', msg=msg,loggedin=logged_in,usrname=username)


@app.route('/userHome/<string:name>', methods=['GET', 'POST'])
def userHome(name):
    createdFiles = []
    for i, s in enumerate(db.session.query(fileMetadata).all()):
        ss = s.__dict__
        if ss["username"] == username:
            # for i,path in os.listdir(os.path.join(os.getcwd(),"static","file_uploads","user_imputed_data",username)):
            createdFiles.append({"file": ss['filename'], "name": ss['name']})
    if request.method == 'POST':
        print("delete button was clicked...")
        print(request.form)
        form_data = [i for i in request.form.keys()]
        if "deletebutton" in form_data:
            createdFiles_ = []
            for idx in createdFiles:
                if idx['name'] in form_data:
                    pass
                else:
                    createdFiles_.append(idx)
            createdFiles = createdFiles_
            print("some files were removed...")
            print(createdFiles)
    if len(createdFiles) == 0:
        lenofdata = "No records found..."
    else:
        lenofdata = ''

    return render_template("userHome.html", user=name, createdFiles=createdFiles, lenofdata=lenofdata ,loggedin=logged_in,usrname=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    print(request.form)
    '''Check if all required fields are entered if not pop-up not entered condition'''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        psw = request.form['password']
        email = request.form['email']
        UserId = request.form['UserId']
        '''Check whether the email is a valid email or not if not make them enter the valid email'''
        if is_valid_username(username):
            if is_valid_email(email):
                res, msg = check_password_strength(psw)
                if res:
                    flag = 0
                    for i, d in enumerate(db.session.query(signup).all()):
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
                            usr_id=UserId,
                            email_id=email,
                            name=username,
                            password=psw
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
    return render_template('register.html', msg=msg,loggedin=logged_in,usrname=username)


@app.route("/logout", methods=['GET'])
def logout():
    global logged_in,username
    logged_in = False
    username = ''
    return redirect('/')

@app.route("/Contact",methods=['GET','POST'])
def Contact():
    if request.method == 'POST':
        feedback = dict(request.form)
        print(feedback)
        msg = Message(
            'EasyFill Feedback',
            sender=config.MAIL_USERNAME,
            recipients=config.MAIL_Recepients
        )
        msg.body = f"Feedback from user:\n name - {feedback['uname']}\n mail - {feedback['email']}\n message - {feedback['subject']}"
        mail.send(msg)
        successtxt = "Message sent successfully. We will get back to you shortly!"
    else:
        successtxt = ''
    return render_template("contact.html",successtxt=successtxt,loggedin=logged_in,usrname=username)

@app.route("/pricing")
def pricing():
    # return render_template("pricing.html")
    return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.run()
    db.create_all()
    app.app_context().push()


