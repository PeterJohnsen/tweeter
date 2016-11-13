#!/usr/bin/env python
from flask import Flask, render_template

from config import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    context = {}
    return render_template('index.html', context=context)


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
