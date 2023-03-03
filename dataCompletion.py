from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/login_page')
def login_page():
    return render_template('login_page.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup_page.html')

if __name__ == '__main__':
    app.debug = True
    app.run()