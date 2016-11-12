from flask import Flask

from config import *

app = Flask(__name__)

@app.route('/', method=['GET'])
def index():
    return "Welcome to Tweeter"


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)




