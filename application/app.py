from flask import Flask, render_template
import sqlite3

# Initialise the flask app
app = Flask(__name__)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)