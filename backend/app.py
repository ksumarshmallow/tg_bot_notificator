import os
from flask import Flask
from backend.routes import app

app = Flask(__name__, static_folder='frontend/public', static_url_path='')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
