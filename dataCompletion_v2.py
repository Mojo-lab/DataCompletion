import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
from werkzeug.utils import secure_filename
import pandas as pd

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/file_uploads'
app.secret_key = 'magic puzzle'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def homepage():
    return render_template('index.html')

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
            print("***"*30)
            print(df)
            return render_template('eda.html')
        else:
            flash("Wrong file format!!!")
            return redirect(request.url)
    else:
        return render_template("demo.html")


if __name__ == '__main__':
    app.debug = True
    app.run()