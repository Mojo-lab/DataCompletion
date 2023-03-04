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
            null_values = pd.DataFrame(df.isnull().sum(),columns = ['values'])
            print(null_values)
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