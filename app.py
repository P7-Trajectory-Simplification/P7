from flask import Flask, request
from flask import render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html.jinja', algorithms=['Ours', 'SQUISH', 'SQUISH-E', 'DP'])

@app.route('/algorithm')
def get_algorithm_ours():
    name = request.args.get("name")
    return {"name": name, "description": f"{name} algorithm"}