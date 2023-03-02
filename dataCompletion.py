from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def homepage():
    print("hello world!!!")
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()