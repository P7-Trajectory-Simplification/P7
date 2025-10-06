from flask import Flask, request
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=['Ours', 'SQUISH', 'SQUISH-E', 'DP'])

@app.route('/algorithm')
def get_algorithm_ours():
    algs = request.args.get("algs")
    start_time = request.args.get("start_time")
    return {"description": algs, "time": start_time}