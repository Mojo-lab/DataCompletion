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
from blog import blogdata
import jwt
from time import time


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
    print(request.args)
    username = request.args.get("user")
    htmlData = {"user":username}
    return render_template('index.html',htmlData=htmlData)

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
        repeat_pwd = request.form['pwd1']
        '''Check whether the email is a valid email or not if not make them enter the valid email'''
        if is_valid_username(username):
            if psw != repeat_pwd:
                msg = "Entered password does not match."
            elif is_valid_email(email):
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
                        msg = Message(
                            'EasyFill User Registration - OTP',
                            sender=config.MAIL_USERNAME,
                            recipients=[email]
                        )
                        msg.body = f"Dear user, kindly use the following OTP to register your account:\n  OTP - 12345"
                        mail.send(msg)
                        return render_template("confirm_user.html",UserId=UserId,email=email,name=username,password=psw,msg='')

            else:
                msg = "Please enter a valid email address"
        else:
            msg = "Please enter a valid username. Only support character not interger or special characters"
    elif request.method == 'POST':
        msg = 'Please fill all the required fields from the form !'
    return render_template('register.html', msg=msg)

@app.route('/confirm_user',methods=['GET','POST'])
def confirm_user():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        psw = request.form['password']
        email = request.form['email']
        UserId = request.form['UserId']
        otp = request.form['otp']
        if str(otp) == '12345':
            pp = signup(
                usr_id=UserId,
                email_id=email,
                name=username,
                password=psw
            )
            db.session.add(pp)
            db.session.commit()
            msg = 'You have successfully registered !'
        return render_template("confirm_user.html", UserId=UserId, email=email, name=username, password=psw,msg=msg)
    else:
        return render_template("confirm_user.html",msg=msg)

@app.route("/forgotpassword",methods=['GET','POST'])
def forgotpassword():
    msg_=''
    if request.method == 'POST':
        userMail = request.form.get("email")


        msg_ = "A new password been sent to your mail."
        msg = Message(
            'EasyFill Password Reset',
            sender=config.MAIL_USERNAME,
            recipients=[userMail]
        )
        rows_changed = signup.query.filter_by(email_id=userMail).update(dict(password='we1c@me@123'))
        db.session.commit()
        msg.body = f"Dear user, kindly use the following password to log into your account:\n  password - we1c@me@123"
        mail.send(msg)
    return render_template('forgotpassword.html',msg=msg_)

def tabledatahtml(createdFiles,user):
    htmltxt = '''<table id="mytable"
             data-toggle="table"
             data-sort-name="name"
             data-sort-order="desc"
             data-show-fullscreen="true"
             data-pagination="true"
             data-page-size="5"
             data-page-list="[5, 10, 20, 50, 100]"
             data-search="true"
             data-show-refresh="true"
             data-show-toggle="true"
             data-show-columns="true"
             data-toolbar="#toolbar">
        <thead>
          <tr>
            <th data-field="state" data-checkbox="true"></th>
            <th data-field="workspaceName" data-sortable="true">Workspace Name</th>
            <th data-field="rawData" data-filter-control="input" data-sortable="true">Raw Data</th>
            <th data-field="imputedData" data-filter-control="select" data-sortable="true">Imputed Data</th>
            <th data-field="fileSize" data-filter-control="select" data-sortable="true">File size</th>
            <th data-field="createdAt" data-filter-control="select" data-sortable="true">Created At</th>
            <th data-field="modifiedAt" data-filter-control="select" data-sortable="true">Modified At</th>
          </tr>
        </thead>
        <tbody>'''
    for f in createdFiles:
        htmltxt_ = f'''
            <tr value="{f['file']}">
                  <td></td>
                    <td><a href="/eda?filepath={f['file']}&name={f['name']}&user={user}">{f['name']}</a></td>
                    <td><a href="/eda?filepath={f['file']}&name={f['name']}&user={user}">/eda/{f['file']}</a></td>
                    <td><a href="/eda?filepath={f['file']}&name={f['name']}&user={user}">/eda/{f['file']}</a></td>
                    <td>200mb</td>
                    <td>feb26</td>
                        <td>feb26</td>
              </tr>'''
        htmltxt = htmltxt + htmltxt_
    html_1 = '''</tbody>
      </table>
        '''
    htmltxt = htmltxt + html_1
    return htmltxt



@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    flag = 0
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email_id = request.form['email']
        psw = request.form['password']
        for i, d in enumerate(db.session.query(signup).all()):
            dd = d.__dict__
            if dd['email_id'] == email_id:
                flag = 1
                if dd['password'] == psw:
                    msg = "Logged in successfully!"
                    username = dd['name']
                    logged_in = "True"
                    createdFiles = []
                    for i, s in enumerate(db.session.query(fileMetadata).all()):
                        ss = s.__dict__
                        if ss["username"] == username:
                            createdFiles.append({"file": ss['filename'], "name": ss['name']})


                    htmltxt = tabledatahtml(createdFiles,username)

                    try:
                        createdFiles
                    except UnboundLocalError:
                        createdFiles = []
                    if len(createdFiles) == 0:
                        lenofdata = "No records found..."
                    else:
                        lenofdata = ''
                    htmlData = {"user":username,"createdFiles":createdFiles,"lenofdata":lenofdata,"tablehtml":htmltxt}
                    return render_template("btTable.html", htmlData=htmlData)
                else:
                    msg = "Password Incorrect"
            else:
                msg ="Invalid Username or EMAIL"
        if flag == 0:
            msg = "Unable to find the email ID. Please register if not"


    return render_template('login.html', msg=msg)

@app.route("/logout", methods=['GET'])
def logout():
    print(request.args)
    return redirect('/')

@app.route("/demo", methods=['GET', 'POST'])
def demo():
    user = request.args.get("user")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
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
            htmlData = {"data":data,"user":user,"file":filename}
            return render_template('eda.html',htmlData=htmlData)
        else:
            flash("Wrong file format!!!")
            return redirect(request.url)
    else:
        htmlData = {"user":user}
        return render_template("demo.html", htmlData=htmlData)


@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    print(request.args)
    username = request.args.get("user")
    if request.method == 'POST':
        ids = request.get_json()
        for idx in ids:
            fileMetadata.query.filter_by(username=username, name=idx).delete()
            db.session.commit()
        createdFiles = []
        hreflinks = []
        for i, s in enumerate(db.session.query(fileMetadata).all()):
            ss = s.__dict__
            if ss["username"] == username:
                createdFiles.append({"name": ss['name'], "file": ss['filename']})

        if len(createdFiles) == 0:
            lenofdata = "No records found..."
            htmltxt = tabledatahtml(createdFiles,username)

        else:
            htmltxt = tabledatahtml(createdFiles,username)
            lenofdata = ''

        return htmltxt
    else:
        createdFiles = []
        hreflinks = []
        for i, s in enumerate(db.session.query(fileMetadata).all()):
            ss = s.__dict__
            if ss["username"] == username:
                createdFiles.append({"name": ss['name'], "file": ss['filename']})
        if len(createdFiles) == 0:
            lenofdata = "No records found..."
            htmltxt = tabledatahtml([],username)
        else:
            htmltxt = tabledatahtml(createdFiles,username)
            lenofdata = ''
        htmlData = {"user":username, "createdFiles":createdFiles, "lenofdata":lenofdata ,"tablehtml":htmltxt}
        return render_template("btTable.html",htmlData=htmlData )


@app.route('/fillna', methods=['GET', 'POST'])
def fillnaValue():
    colours = ['Mean', 'Median', 'Mode', 'None']
    fillmeth = ['Categorical', 'Continuous']
    col = session.get("Column_names")
    folder_path = session.get('folder_path')
    cols = eval(col)
    download_file_status = ""
    downloadlink = ''
    downloadmessage = ''
    errMsg = ''
    filename = request.args.get("filename")
    user = request.args.get("user")
    workSpaceName = request.args.get("name")
    print(request.args)
    if request.method == 'POST':
        fill_methods = []
        folder_path = session.get('folder_path')
        # filename = session.get("filename")
        col = session.get("Column_names")
        for val in request.values.items():
            fill_methods.append(val)
        try:
            df = dataCompletion_fill.main(folder_path, col, fill_methods)
            print(df.isnull().sum())
            filled_dataset_path = f"static/file_uploads/filled_datasets/{user}"
            try:
                os.mkdir(filled_dataset_path)
            except FileExistsError:
                pass
            filled_dataset_path = filled_dataset_path+f"/{filename}"
            print(f"file saved at this loc - {filled_dataset_path}")
            if '.csv' in folder_path:
                df.to_csv(filled_dataset_path, index=False)
            else:
                df.to_excel(filled_dataset_path, index=False)
            print(f"file saved at this loc - {filled_dataset_path}")
            download_file_status = "Download File"
            downloadlink = f'/getdata?user={user}&filename={filename}'
            downloadmessage = 'EasyFill has finished filling the missing values!'
        except TypeError:
            errMsg = f"The entered data type one or more column is wrong. Please check it again."
    else:
        print("Method GET")
    htmlData = {"colours":colours, "cols":cols, "filestatus":download_file_status,"errMsg":errMsg,
                "downloadlink":downloadlink, "downloadmessage":downloadmessage, "fillmeth":fillmeth,"user":user,"filename":filename,"workSpaceName":workSpaceName}
    return render_template('fillna.html',htmlData=htmlData)

@app.route("/getdata")
def getdata():
    folder_path = session.get('folder_path')
    print(session)
    print(request.args)
    user = request.args.get("user")
    filename = request.args.get("filename")
    folder_path = f"static/file_uploads/filled_datasets/{user}/{filename}"
    if '.csv' in folder_path:
        file_type = 'text/csv'
    else:
        file_type = "text/xlsx"
    return send_file(
        folder_path,
        mimetype=file_type,
        download_name='EasyFilledData.csv',
        as_attachment=True)


def bt5Tablegen(filepath):
    if ".csv" in filepath:
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath, engine="openpyxl")

    tableheader = '''<table
            data-toggle="table"
                id="table-container"
              data-toolbar="#toolbar"
              data-search="true"
              data-show-refresh="true"
              data-show-toggle="true"
              data-show-fullscreen="true"
              data-show-columns="true"
              data-show-columns-toggle-all="true"
              data-detail-view="false"
              data-show-export="true"
              data-click-to-select="true"
              data-minimum-count-columns="2"
              data-show-pagination-switch="true"
              data-pagination="true"
              data-id-field="id"
              data-page-list="[5,10, 25, 50, 100, all]"
                data-show-footer="false"
               locale="en-US">

                    <thead class="bg-secondary text-white">'''
    html_cont = df.to_html()
    html_cont = html_cont.split("<thead>")[1]
    html_cont = tableheader + html_cont
    return html_cont


@app.route('/eda', methods=['GET'])
def eda():
    spacename = request.args.get('name')
    filename = request.args.get("filepath")
    username = request.args.get("user")
    print(request.args)
    filepath = f'static/file_uploads/user_raw_data/{username}/{filename}'
    session['folder_path'] = filepath
    data = null_value_graphs(filepath, filename,session)
    homeTable = bt5Tablegen(filepath)
    easyFilledPath = f"static/file_uploads/filled_data/{username}/{filename}"
    easyFilled = str(os.path.exists(easyFilledPath)).lower()
    htmlData = {"data":data, "user":username, "homeTable":homeTable,"filename":filename,"workSpaceName":spacename,"easyFilled":easyFilled}
    return render_template("multiHome.html",htmlData=htmlData)

@app.route('/multiHome', methods=['GET'])
def multiHome():
    filename = request.args.get("filename")
    username = request.args.get("user")
    spacename = request.args.get("name")
    filepath = f'static/file_uploads/user_raw_data/{username}/{filename}'
    data = null_value_graphs(filepath, filename,session)
    homeTable = bt5Tablegen(filepath)
    easyFilledPath = f"static/file_uploads/filled_datasets/{username}/{filename}"
    easyFilled = str(os.path.exists(easyFilledPath)).lower()
    htmlData = { "data":data, "user":username, "homeTable":homeTable,"filename":filename,"workSpaceName":spacename,"easyFilled":easyFilled}
    return render_template("multiHome.html",htmlData =htmlData)



@app.route('/edareport',methods=['GET'])
def edareport():
    filename = request.args.get("filename")
    username = request.args.get("user")
    spacename = request.args.get("name")
    filepath = f'static/file_uploads/user_raw_data/{username}/{filename}'
    filepath = session.get("folder_path")
    data = eda_report(filepath)
    htmlData = {'data':data[0],'data1':data[1],'data2':data[2],'catdata' : data[2][1],'contdata' : data[2][2],
                "user":username,"filename":filename,"workSpaceName":spacename}
    return render_template('edareport1.html',htmlData = htmlData)


@app.route('/newwork', methods=['GET', 'POST'])
def newwork():
    if request.method == 'POST':
        print(request.form)
        print(request.args)
        name = request.form['fname']
        file = request.files['file']
        username = request.args.get('user')
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

        username = request.args.get("user")
        workSpaceName = name
        session['folder_path'] = filepath
        data = null_value_graphs(filepath, filename,session)
        htmlData = {"data":data,"user":username,"filename":filename,"workSpaceName":workSpaceName}
        return render_template('multiHome.html', htmlData=htmlData)
    else:
        username = request.args.get("user")
        filename = request.args.get("filename")
        workSpaceName = request.args.get("name")
        htmlData = {"user":username,"filename":filename,"workSpaceName":workSpaceName}
        return render_template('newwork.html',htmlData=htmlData)


@app.route("/Contact",methods=['GET','POST'])
def Contact():
    if request.method == 'POST':
        feedback = dict(request.form)
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
    user = request.args.get("user")
    htmlData = {"user":user,"successtxt":successtxt}
    return render_template("contact.html",htmlData=htmlData)

@app.route("/pricing")
def pricing():
    # return render_template("pricing.html")
    return redirect('/')

@app.route("/subscribe",methods=['GET','POST'])
def subscribe():
    print("in subscribe func")
    print(request.form)
    print(request.method)
    print(request.data)
    if request.method == 'POST':
        print(request.form)
    else:
        pass
    return redirect('/')


@app.route("/blog",methods=['GET','POST'])
def blog():
    user = request.args.get("user")
    print(request.args)
    htmlData = {"blogdata":blogdata,"user":user}
    return render_template('/blog.html',htmlData=htmlData)

@app.route("/blog/<string:articleid>",methods=['GET'])
def article(articleid):
    print(articleid)
    user = request.args.get("user")
    print(request.args)
    htmlData = {"user":user}
    print(htmlData)
    return render_template(articleid,htmlData=htmlData)


if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)
    db.create_all()
    app.app_context().push()
