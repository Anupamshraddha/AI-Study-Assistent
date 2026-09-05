from flask import Flask

app = Flask(__name__)

# your existing routes here


if __name__ == "__main__":
    app.run(debug=True)
